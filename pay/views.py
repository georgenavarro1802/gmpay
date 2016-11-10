import hashlib
import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render

from pay.forms import RegistroFormulario
from pay.infopages import bad_json
from pay.models import TipoIdentificacion, Cliente, Operacion


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/panel")
    return render_to_response("index.html",
                              {
                                  "formulario_registro": RegistroFormulario(initial={
                                      "tipoidentificacion": TipoIdentificacion.objects.first()
                                  })
                              })


def registro(request):
    if request.method == 'POST':
        formulario = RegistroFormulario(request.POST)
        if formulario.is_valid():
            datos = formulario.cleaned_data

            username = datos['nombre'].replace(" ", "").lower()
            correo = datos['correo']
            clave = datos['clave']

            if User.objects.filter(Q(username=username) | Q(email=correo)).exists():
                messages.error(request, "Ya existe este usuario")
                if 'next' in request.POST:
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return HttpResponseRedirect("/")

            usuario = User.objects.create_user(username=username, email=correo, password=clave)
            nombre = datos['nombre'].split(" ")
            usuario.first_name = nombre[0]
            if len(nombre) > 1:
                usuario.last_name = " ".join(nombre[1:])
            usuario.save()

            cliente = Cliente(usuario=usuario,
                              tipoidentificacion=datos['tipoidentificacion'],
                              identificacion=datos['identificacion'],
                              vendedor='000000',
                              saldo=Decimal('10'))
            cliente.save()
            cliente.vendedor = str(cliente.id).zfill(6)
            cliente.save()

            usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, usuario)
            if 'next' in request.POST:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect("/panel")
        else:
            messages.error(request, "Datos Incorrectos")
            if 'next' in request.POST:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


@login_required(login_url='/login')
def panel(request):
    cliente = Cliente.objects.filter(usuario=request.user)[0]

    if request.method == 'POST':
        try:
            with transaction.atomic():
                valor = Decimal(request.POST['valor'])
                descr = request.POST['descripcion']
                weburl = hashlib.sha1("%d %s %s" % (cliente.id, str(valor), descr)).hexdigest()[:10]

                operacion = Operacion(cliente=cliente, valor=valor, descripcion=descr, weburl=weburl)
                operacion.save()

                return HttpResponse(json.dumps({"url": "http://%s/%s" % (request.get_host(), weburl)}),
                                    content_type="application/json")
        except Exception as ex:
            messages.error(request, "Debe llenar todos los campos")
            return bad_json(ex.message)
    else:
        return render(request, "panel.html", {"cliente": cliente, "request": request})


def entrar(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/panel')

    if request.method == 'POST':
        email = request.POST['usuario']
        clave = request.POST['clave']
        if User.objects.filter(email=email).exists():
            u = User.objects.filter(email=email)[0]
            usuario = authenticate(username=u.username, password=clave)
            if usuario:
                login(request, usuario)
                if 'next' in request.POST:
                    return HttpResponseRedirect(request.POST['next'])
                return HttpResponseRedirect('/')
            else:
                messages.error(request, "Credenciales incorrectas")
                return HttpResponseRedirect(
                    '/login%s' % ("?next=%s" % (request.POST['next']) if 'next' in request.POST else ""))
        else:
            messages.error(request, "No existe este usuario")
            return HttpResponseRedirect(
                '/login%s' % ("?next=%s" % (request.POST['next']) if 'next' in request.POST else ""))
    else:
        datos = {}
        if 'next' in request.GET:
            datos['next'] = request.GET['next']
        return render(request, 'login.html', datos)


def salir(request):
    logout(request)
    if 'next' in request.GET:
        return HttpResponseRedirect("/login?next=%s" % (request.GET['next']))
    return HttpResponseRedirect("/")


def olvido(request):
    return render_to_response('olvido.html')


@login_required(login_url='/login')
def perfil(request):
    return render_to_response('perfil.html')
