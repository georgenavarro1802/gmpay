from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models

import hashlib
from django.db.models import Q


class TipoIdentificacion(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo Identificacion"
        verbose_name_plural = "Tipos de Identificacion"


class Cliente(models.Model):
    usuario = models.OneToOneField(User, related_name="profile", unique=False)
    tipoidentificacion = models.ForeignKey(TipoIdentificacion)
    identificacion = models.CharField(max_length=20)
    vendedor = models.CharField(max_length=8)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    def api_key(self):
        if self.apikey_set.exists():
            return self.apikey_set.all()[:1].get()
        else:
            a = APIKey(cliente=self,
                       key=hashlib.sha1("%d-%s-%s" % (self.id, self.full_name(), datetime.today())).hexdigest())
            a.save()
            return a

    def renew_api_key(self):
        if self.apikey_set.exists():
            self.apikey_set.all().delete()

        a = APIKey(cliente=self,
                   key=hashlib.sha1("%d-%s-%s" % (self.id, self.full_name(), datetime.today())).hexdigest())
        a.save()
        return a

    def email(self):
        return self.usuario.email

    def full_name(self):
        return self.usuario.get_full_name()

    def __str__(self):
        return self.usuario.get_full_name()

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def pagos_realizados(self):
        return self.pago_set.all().order_by('-fecha')[:20]

    def muchos_pagos(self):
        return self.pago_set.all().count() > 20

    def cobros_realizados(self):
        return Pago.objects.filter(operacion__cliente=self).order_by('-fecha')[:20]

    def muchos_cobros(self):
        return Pago.objects.filter(operacion__cliente=self).count() > 20

    def gravatar(self):
        return hashlib.md5(self.email()).hexdigest()

    def tiene_operaciones(self):
        return Pago.objects.filter(Q(comprador=self) | Q(operacion__cliente=self)).exists()


class Operacion(models.Model):
    cliente = models.ForeignKey(Cliente)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    weburl = models.CharField(max_length=10)

    def __str__(self):
        return "%s - %10.2f - %s - %s" % (self.cliente, float(self.valor), 
                                          self.descripcion, self.fecha.strftime("%d-%m-%Y"))

    class Meta:
        verbose_name = "Operacion"
        verbose_name_plural = "Operaciones"


class Pago(models.Model):
    operacion = models.ForeignKey(Operacion)
    comprador = models.ForeignKey(Cliente)
    fecha = models.DateTimeField(auto_now_add=True)
    pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def json_repr(self):
        return {'fecha': self.fecha.strftime("%d-%m-%Y"),
                'valor': str(self.pagado),
                'cliente': self.comprador.full_name(),
                'identificacion': self.comprador.identificacion,
                'tipoidentificacion': self.comprador.tipoidentificacion.nombre}

    def __str__(self):
        return "%s - %s - %s" % (self.operacion, self.comprador, self.fecha.strftime("%d-%m-%Y"))

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"


class Deposito(models.Model):
    cliente = models.ForeignKey(Cliente)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=100)

    def __str__(self):
        return "Deposito %s: %10.2f" % (self.cliente, float(self.valor))

    class Meta:
        verbose_name = "Deposito"
        verbose_name_plural = "Despositos"


class APIKey(models.Model):
    cliente = models.ForeignKey(Cliente)
    key = models.CharField(max_length=40)

    def __str__(self):
        return "%s: %s" % (self.cliente, self.key)
