# -*- coding: UTF-8 -*-

from django import forms
from pay.models import TipoIdentificacion


class RegistroFormulario(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Su Nombre y Apellidos'}))
    correo = forms.EmailField(label="Correo", required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Su Correo Electronico'}))
    tipoidentificacion = forms.ModelChoiceField(TipoIdentificacion.objects.all(),label=u"Tipo de Identificación", required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    identificacion = forms.CharField(max_length=20, label=u"Identificación", required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Su Identificacion'}))
    clave = forms.CharField(max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control'}),label='Clave',required=True)


class ContactoForm(forms.Form):
    nombre = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Su Nombre'}))
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Correo'}))
    mensaje = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Mensaje', 'rows':'5'}))