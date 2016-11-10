from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render

from pagacompa.settings import EMAIL_ACTIVE
from pay.forms import RegistroFormulario
from pay.infopages import add_default_data
from pay.models import Operacion, Cliente, Pago, Deposito, TipoIdentificacion
from pay.tareas import send_html_mail


def fix_spaces(s):
    return s.replace("_", " ")


COMISION_TRANSACCION = Decimal('0.25')
CLIENTE_MANAGER_ID = 3


def view(request, weburl):
    data = {}
    add_default_data(request, data)
    if Operacion.objects.filter(weburl=weburl).exists():
        operacion = Operacion.objects.filter(weburl=weburl)[:1].get()

        if request.method == 'POST':
            try:
                # Confirmar clave y pagar
                clave = request.POST['clave']
                usuario = authenticate(username=request.user.username, password=clave)
                if usuario and usuario.id == data['cliente'].usuario.id:
                    # Validada Clave
                    pago = Pago(operacion=operacion, comprador=data['cliente'],
                                pagado=operacion.valor - COMISION_TRANSACCION)
                    pago.save()

                    vendedor = operacion.cliente
                    vendedor.saldo = vendedor.saldo + pago.pagado
                    vendedor.save()

                    cliente = pago.comprador
                    cliente.saldo = cliente.saldo - operacion.valor
                    cliente.save()

                    # DEPOSITAR COMISION
                    manager = Cliente.objects.get(pk=CLIENTE_MANAGER_ID)
                    manager.saldo = manager.saldo + COMISION_TRANSACCION
                    manager.save()

                    deposito = Deposito(cliente=manager,
                                        valor=COMISION_TRANSACCION,
                                        motivo="COMISION PAGO #%d" % pago.id)
                    deposito.save()
                    messages.info(request,
                                  "Realizado pago en Operacion: %s por %10.2f" % (operacion.descripcion,
                                                                                  float(operacion.valor)))
    
                    # Enviar correo is esta activo
                    if EMAIL_ACTIVE:
                        # Al Pagador
                        send_html_mail("Pago realizado PAGACOMPA", "emails/pagorealizado.html", {"pago": pago},
                                       [pago.comprador.email()])
                        # Al Cobrador
                        send_html_mail("Pago recibido PAGACOMPA", "emails/pagorecibido.html", {"pago": pago},
                                       [pago.operacion.cliente.email()])
    
                    if 'redirect' in request.POST:
                        return HttpResponseRedirect("%s?weburl=%s?pagado" % (request.POST['redirect'],
                                                                             operacion.weburl))
                    else:
                        return HttpResponseRedirect("/panel")
                else:
                    messages.error(request, "No se puede realizar el pago, la clave no coincide.")
                    return HttpResponseRedirect("/%s" % weburl)
            
            except Exception:
                messages.error(request, "No se pudo realizar el pago, error de comunicacion.")
                return HttpResponseRedirect("/%s" % weburl) 
        else:
            data['operacion'] = operacion
            if 'redirect' in request.GET:
                data['redirect'] = request.GET['redirect']

            data['puede_pagar'] = False
            if 'cliente' in data:
                data['puede_pagar'] = data['cliente'].saldo >= operacion.valor

            data['formulario_registro'] = RegistroFormulario(initial={
                "tipoidentificacion": TipoIdentificacion.objects.first()
            })

            return render(request, "pago/pago.html", data)
    else:
        return render(request, "pago/noexiste.html", data)
