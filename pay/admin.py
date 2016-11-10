from django.contrib import admin

from pay.models import TipoIdentificacion, Cliente, Operacion, Pago

admin.site.register(TipoIdentificacion)


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'tipoidentificacion', 'identificacion', 'vendedor', 'saldo')


admin.site.register(Cliente, ClienteAdmin)


class OperacionAdmin(admin.ModelAdmin):
    list_display = ('weburl', 'cliente', 'valor', 'descripcion', 'fecha')


admin.site.register(Operacion, OperacionAdmin)


class PagoAdmin(admin.ModelAdmin):
    list_display = ("operacion", "comprador", "fecha", "pagado")


admin.site.register(Pago, PagoAdmin)
