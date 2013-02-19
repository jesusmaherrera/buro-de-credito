#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
#MODELOS Y FORMULARIOS DEL PROYECTO
from models import *
from forms import *
#MODELOS DE EL PROYECTO DE CITIES_LIGHT
from cities_light.models import City

import datetime, time
from django.db.models import Q

from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory

#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from django.db import connection

##########################################
## 										##
##               LOGIN     			    ##
##										##
##########################################

def ingresar(request):
	# if not request.user.is_anonymous():
	# 	return HttpResponseRedirect('/')
	if request.method == 'POST':
		formulario = AuthenticationForm(request.POST)
		if formulario.is_valid:
			usuario = request.POST['username']
			clave = request.POST['password']
			acceso = authenticate(username=usuario, password=clave)
			if acceso is not None:
				if acceso.is_active:
					login(request, acceso)
					return HttpResponseRedirect('/')
				else:
					return render_to_response('noactivo.html', context_instance=RequestContext(request))
			else:
				return render_to_response('login.html',{'form':formulario, 'message':'Nombre de usaurio o password no validos',}, context_instance=RequestContext(request))
	else:
		formulario = AuthenticationForm()
	return render_to_response('login.html',{'form':formulario, 'message':'',}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')

##########################################
## 										##
##               CLIENTE			    ##
##										##
##########################################

@login_required(login_url='/login/')
def cliente_manageView(request, id = None, template_name='clientes/cliente.html'):
	if id:
		cliente = get_object_or_404(Cliente, pk=id)
	else:
		cliente = Cliente()

	msg = '' 

	if request.method == 'POST':
		Cliente_form = ClienteManageForm(request.POST, request.FILES, instance=cliente)

		if Cliente_form.is_valid():
			cliente_O = Cliente_form.save(commit = False)
			clientesIguales = Cliente.objects.filter(city = cliente_O.city).filter(codigo_postal 	= 	cliente_O.codigo_postal).filter(dir_colonia		=	cliente_O.dir_colonia).filter(dir_calle		=	cliente_O.dir_calle).filter(dir_poblacion	=	cliente_O.dir_poblacion)

			if clientesIguales.count() > 1:
				msg = 'Ya existe otro cliente con la misma direccion porfavor revisa bien los datos!'
			else:
				if request.user.has_perm('compras_app.change_cliente'):
					cliente_O.save()

				return HttpResponseRedirect('/clientes/')
			
			c = {'cliente_form': Cliente_form, 'msg':msg}
			return render_to_response(template_name, c, context_instance=RequestContext(request))
	else:
		if request.user.has_perm('compras_app.add_cliente'):
			Cliente_form = ClienteManageForm(instance=cliente)
		else:
			return HttpResponseRedirect('/clientes/')
		
	c = {'cliente_form': Cliente_form, }

	return render_to_response(template_name, c, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def clientesView(request, id = None, template_name='clientes/clientes.html'):
	
	clientesIguales = None
	msg = '' 
	if request.method == 'POST':
		Cliente_form = ClientesBusquedaForm(request.POST, request.FILES)

		if Cliente_form.is_valid():
			cliente_O = Cliente_form.save(commit = False)
			
			if cliente_O.nombre == '':
				cliente_O.nombre = '*'
			if cliente_O.dir_colonia == '':
				cliente_O.dir_colonia = '*'
			if cliente_O.dir_calle == '':
				cliente_O.dir_calle = '*'
			if cliente_O.codigo_postal == '':
				cliente_O.codigo_postal = '*'
			if cliente_O.dir_poblacion == '':
				cliente_O.dir_poblacion ='*'

			if cliente_O.city == None:
				#clientesIguales = Cliente.objects.filter(Q(nombre__icontains = cliente_O.nombre)|).filter(dir_colonia__icontains = cliente_O.dir_colonia).filter(dir_no_interior__icontains = cliente_O.dir_no_interior).filter(dir_no_exterior__icontains = cliente_O.dir_no_exterior).filter(codigo_postal__icontains = cliente_O.codigo_postal).filter(dir_calle__icontains = cliente_O.dir_calle)
				clientesIguales = Cliente.objects.filter(
					(Q(nombre__icontains = cliente_O.nombre) & Q(telefono__icontains = cliente_O.telefono))|
					Q(dir_colonia__icontains = cliente_O.dir_colonia)|
					Q(dir_colonia__icontains = cliente_O.dir_poblacion)|  
					(Q(dir_calle__icontains = cliente_O.dir_calle)& (Q(dir_no_interior__icontains = cliente_O.dir_no_interior)| Q(dir_no_exterior__icontains = cliente_O.dir_no_exterior)))|
					Q(codigo_postal__icontains = cliente_O.codigo_postal)
					)
			else:
				clientesIguales = Cliente.objects.filter(
					(Q(nombre__icontains = cliente_O.nombre) & Q(telefono__icontains = cliente_O.telefono))|
					Q(dir_colonia__icontains = cliente_O.dir_colonia)|  
					(Q(dir_calle__icontains = cliente_O.dir_calle)& (Q(dir_no_interior__icontains = cliente_O.dir_no_interior)| Q(dir_no_exterior__icontains = cliente_O.dir_no_exterior)))|
					Q(codigo_postal__icontains = cliente_O.codigo_postal)).filter(city = cliente_O.city)
					#Cliente.objects.filter(nombre__icontains = cliente_O.nombre).filter(dir_colonia__icontains = cliente_O.dir_colonia).filter(dir_no_interior__icontains = cliente_O.dir_no_interior).filter(dir_no_exterior__icontains = cliente_O.dir_no_exterior).filter(codigo_postal__icontains = cliente_O.codigo_postal).filter(dir_calle__icontains = cliente_O.dir_calle).filter(city = cliente_O.city)
			
			if clientesIguales.count() > 1:
				msg = 'Existe otro cliente con estos datos'

			
			c = {'cliente_form': Cliente_form, 'msg':msg, 'clientesIguales':clientesIguales,}
			return render_to_response(template_name, c, context_instance=RequestContext(request))
	else:
		clientesIguales = Cliente.objects.all()		
		Cliente_form = ClientesBusquedaForm()
	
	#clientesIguales = Cliente.objects.all()

	paginator = Paginator(clientesIguales, 20) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		clientes = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    clientes = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    clientes = paginator.page(paginator.num_pages)

	c = {'cliente_form':Cliente_form, 'clientesIguales':clientes,}
  	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def clientes_deleteView(request, id = None, template_name='clientes/clientes.html'):
	if request.user.has_perm('compras_app.delete_cliente'):
		cliente = get_object_or_404(Cliente, pk=id)
		cliente.delete()

	return HttpResponseRedirect('/clientes/')

##########################################
## 										##
##               CIUDAD  			    ##
##										##
##########################################

@login_required(login_url='/login/')
def ciudad_manageView(request, id = None, template_name='ciudades/ciudad.html'):
	if id:
		ciudad = get_object_or_404(City, pk=id)
	else:
		ciudad = City()

	if request.method == 'POST':
		Ciudad_form = CiudadManageForm(request.POST, request.FILES, instance=ciudad)

		if Ciudad_form.is_valid():
			if request.user.has_perm('compras_app.change_city'):
				Ciudad_form.save()
			
			return HttpResponseRedirect('/ciudades/')
	else:
		if request.user.has_perm('compras_app.add_city'):
			Ciudad_form = CiudadManageForm(instance=ciudad)
		else:
			return HttpResponseRedirect('/ciudades/')

	c = {'ciudad_form': Ciudad_form, }

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def ciudades_View(request, template_name='ciudades/ciudades.html'):
	try: 
		filtro = request.GET['filtro']
	except:
		filtro = ''
	ciudades_list = City.objects.filter(name__icontains=filtro).filter(country__name='Mexico')

	paginator = Paginator(ciudades_list, 20) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		ciudades = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    ciudades = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    ciudades = paginator.page(paginator.num_pages)

	c = {'ciudades':ciudades,'filtro':filtro,'msg':ciudades.count}
  	return render_to_response(template_name, c, context_instance=RequestContext(request))

def ajax_View(request, id=None):
	if id:
		compra = get_object_or_404(Compra, pk=id)
	else:
		compra = Compra()

 	if request.method == 'POST':
 		form = Compra_form = CompraManageForm(request.POST, request.FILES, instance=compra)
 		if form.is_valid():
 			cliente_nombre = form.cliente.nombre
 			return HttpResponse('Se lececciono el cliente :[%s]'% cliente_nombre, mimetype="text/plain") 
 		#else:
 		#	HttpResponse('ERROR!! NO SE Guardado correctamente')

##########################################
## 										##
##               CREDITO  			    ##
##										##
##########################################

@login_required(login_url='/login/')
def creditosView(request, id = None, template_name='creditos/creditos.html'):
	
	clientesIguales = None
	msg = '' 
	if request.method == 'POST':
		creditos_form = CreditoForm(request.POST)
		Cliente_form = ClientesBusquedaForm(request.POST)

		if Cliente_form.is_valid():
			cliente_O = Cliente_form.save(commit = False)
			
			if cliente_O.nombre == '':
				cliente_O.nombre = '*'
			if cliente_O.dir_colonia == '':
				cliente_O.dir_colonia = '*'
			if cliente_O.dir_calle == '':
				cliente_O.dir_calle = '*'
			if cliente_O.codigo_postal == '':
				cliente_O.codigo_postal = '*'
			if cliente_O.dir_poblacion == '':
				cliente_O.dir_poblacion ='*'

			if cliente_O.city == None:
				#clientesIguales = Cliente.objects.filter(Q(nombre__icontains = cliente_O.nombre)|).filter(dir_colonia__icontains = cliente_O.dir_colonia).filter(dir_no_interior__icontains = cliente_O.dir_no_interior).filter(dir_no_exterior__icontains = cliente_O.dir_no_exterior).filter(codigo_postal__icontains = cliente_O.codigo_postal).filter(dir_calle__icontains = cliente_O.dir_calle)
				clientesIguales = Credito.objects.filter(
					(Q(cliente__nombre__icontains = cliente_O.nombre) & Q(cliente__telefono__icontains = cliente_O.telefono))|
					Q(cliente__dir_colonia__icontains = cliente_O.dir_colonia)|
					Q(cliente__dir_colonia__icontains = cliente_O.dir_poblacion)|  
					(Q(cliente__dir_calle__icontains = cliente_O.dir_calle)& (Q(cliente__dir_no_interior__icontains = cliente_O.dir_no_interior)| Q(cliente__dir_no_exterior__icontains = cliente_O.dir_no_exterior)))|
					Q(cliente__codigo_postal__icontains = cliente_O.codigo_postal)
					)
			else:
				clientesIguales = Credito.objects.filter(
					(Q(cliente__nombre__icontains = cliente_O.nombre) & Q(cliente__telefono__icontains = cliente_O.telefono))|
					Q(cliente__dir_colonia__icontains = cliente_O.dir_colonia)|  
					(Q(cliente__dir_calle__icontains = cliente_O.dir_calle)& (Q(cliente__dir_no_interior__icontains = cliente_O.dir_no_interior)| Q(cliente__dir_no_exterior__icontains = cliente_O.dir_no_exterior)))|
					Q(cliente__codigo_postal__icontains = cliente_O.codigo_postal)).filter(cliente__city = cliente_O.city)
					#Cliente.objects.filter(nombre__icontains = cliente_O.nombre).filter(dir_colonia__icontains = cliente_O.dir_colonia).filter(dir_no_interior__icontains = cliente_O.dir_no_interior).filter(dir_no_exterior__icontains = cliente_O.dir_no_exterior).filter(codigo_postal__icontains = cliente_O.codigo_postal).filter(dir_calle__icontains = cliente_O.dir_calle).filter(city = cliente_O.city)
			
			if clientesIguales.count() > 1:
				msg = 'Existe otro cliente con estos datos'

			
			c = {'cliente_form': Cliente_form, 'creditos_form':creditos_form, 'msg':msg, 'creditosIguales':clientesIguales,}
			return render_to_response(template_name, c, context_instance=RequestContext(request))
	else:
		clientesIguales = Credito.objects.all()
		Cliente_form = ClientesBusquedaForm()
		creditos_form = CreditoForm()
	
	#clientesIguales = Cliente.objects.all()

	paginator = Paginator(clientesIguales, 20) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		clientes = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    clientes = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    clientes = paginator.page(paginator.num_pages)

	c = {'cliente_form':Cliente_form, 'creditosIguales':clientes, 'creditos_form':creditos_form,}
  	return render_to_response(template_name, c, context_instance=RequestContext(request))