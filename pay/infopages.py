from datetime import datetime
from decimal import Decimal
import hashlib
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from pagacompa.settings import EMAIL_HOST_USER, CONTACTO_FORM, EMAIL_ACTIVE
from pay.forms import ContactoForm
from pay.models import Cliente, Operacion
from pay.tareas import send_html_mail


def add_default_data(request, data):
    if request.user.is_authenticated():
        cliente = Cliente.objects.filter(usuario=request.user)[0]
        data.update({
            "cliente": cliente,
            "request": request,
            "email_host_user": "serviciocliente@gmsoftsolution.com"
        })


@login_required(login_url="/login")
def api_renew(request):
    try:
        data = {}
        add_default_data(request, data)
        data['cliente'].renew_api_key()
        return HttpResponseRedirect("/api")
    except Exception:
        return HttpResponseRedirect("/")


def chequeo_formato(obj, formato, parent=[]):
    for k in formato:
        if type(k) == tuple:
            m = k[0]  # master
            p = k[1]  # properties
            o = obj[m]
            if type(o) == dict:
                c, r = chequeo_formato(o, p, parent + [m])
                if not c:
                    return (False, r)
            elif type(o) == list:
                for j in o:
                    c, r = chequeo_formato(j, p, parent + [m])
                    if not c:
                        return (False, r)
        else:
            if not k in obj:
                return (False, "Falta '%s'" % (".".join(parent + [k])))
    return (True, "")


def bad_json(error):
    return HttpResponse(json.dumps({"result": "bad", "error": error}), content_type="application/json")


def ok_json(data):
    res = {"result": "ok"}
    res.update(data)
    return HttpResponse(json.dumps(res), content_type="application/json")


FORMATO_CREATE = ('apikey', 'valor', 'descripcion')

FORMATO_QUERY = ('apikey', 'weburl')

FORMATO_INFO = ('apikey',)


def crear_operacion_json(data, cliente):
    try:
        valor = Decimal(data['valor'])
        descr = data['descripcion']
        weburl = hashlib.sha1("%d %s %s" % (cliente.id, str(valor), descr)).hexdigest()[:10]

        operacion = Operacion(cliente=cliente, valor=valor, descripcion=descr, weburl=weburl)
        operacion.save()

        return operacion, ""
    except Exception as ex:
        return (None, str(ex))


def consulta_operacion_json(data, cliente):
    if Operacion.objects.filter(weburl=data['weburl'], cliente=cliente).exists():
        return (Operacion.objects.filter(weburl=data['weburl'], cliente=cliente)[:1].get(), "")
    else:
        return (None, "No existe esa operacion")


@csrf_exempt
def api_create(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps(
            {
                "api": "PAGACOMPA API Version 1.0",
                "error": "Requerimientos solo por metodo POST"
            }), content_type="application/json")
    else:
        data = request.read()
        try:
            obj = json.loads(data)
            chequeo, resultados = chequeo_formato(obj, FORMATO_CREATE)
            if chequeo:
                if Cliente.objects.filter(apikey__key=obj['apikey']).exists():
                    cliente = Cliente.objects.filter(apikey__key=obj['apikey'])[:1].get()
                    f, error = crear_operacion_json(obj, cliente)
                    if f:
                        return ok_json({'weburl': f.weburl})
                    else:
                        return bad_json(error)
                else:
                    return bad_json("API key incorrecta")
            else:
                return bad_json("Datos incompletos, %s" % (resultados))
        except Exception as ex:
            return bad_json("Error proceso: %s" % (ex))


@csrf_exempt
def api_query(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps(
            {
                "api": "PAGACOMPA API Version 1.0",
                "error": "Requerimientos solo por metodo POST"
            }), content_type="application/json")
    else:
        data = request.read()
        try:
            obj = json.loads(data)
            chequeo, resultados = chequeo_formato(obj, FORMATO_QUERY)
            if chequeo:
                if Cliente.objects.filter(apikey__key=obj['apikey']).exists():
                    cliente = Cliente.objects.filter(apikey__key=obj['apikey'])[:1].get()
                    o, error = consulta_operacion_json(obj, cliente)
                    if o:
                        return ok_json({'fecha': o.fecha.strftime("%d-m-%Y"),
                                        'weburl': o.weburl,
                                        'descripcion': o.descripcion,
                                        'valor': str(o.valor),
                                        'pagos': [p.json_repr() for p in o.pago_set.all()]})
                    else:
                        return bad_json(error)
                else:
                    return bad_json("API key incorrecta")
            else:
                return bad_json("Datos incompletos, %s" % (resultados))
        except Exception as ex:
            return bad_json("Error proceso: %s" % (ex))


@csrf_exempt
def api_info(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps(
            {
                "api": "PAGACOMPA API Version 1.0",
                "error": "Requerimientos solo por metodo POST"
            }), content_type="application/json")
    else:
        data = request.read()
        try:
            obj = json.loads(data)
            chequeo, resultados = chequeo_formato(obj, FORMATO_INFO)
            if chequeo:
                if Cliente.objects.filter(apikey__key=obj['apikey']).exists():
                    cliente = Cliente.objects.filter(apikey__key=obj['apikey'])[:1].get()
                    return ok_json({'cliente': cliente.full_name(),
                                    'identificacion': cliente.identificacion,
                                    'tipoidentificacion': cliente.tipoidentificacion.nombre,
                                    'saldo': str(cliente.saldo)})
                else:
                    return bad_json("API key incorrecta")
            else:
                return bad_json("Datos incompletos, %s" % (resultados))
        except Exception as ex:
            return bad_json("Error proceso: %s" % (ex))
