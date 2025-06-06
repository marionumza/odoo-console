#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para operar Odoo desde la consola
Ejemplo básico para crear órdenes de venta y realizar operaciones
"""

import xmlrpc.client
import json
import os
from dotenv import load_dotenv
from datetime import datetime

class OdooConnector:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv('ODOO_URL')
        self.db = os.getenv('ODOO_DB')
        self.username = os.getenv('ODOO_USERNAME')
        self.password = os.getenv('ODOO_PASSWORD')
        
        # Conexiones XML-RPC
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        self.uid = None
        
    def connect(self):
        """Conectar con Odoo"""
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print(f"✅ Conectado exitosamente a Odoo como {self.username}")
                return True
            else:
                print("❌ Error de autenticación")
                return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def execute(self, model, method, *args, **kwargs):
        """Ejecutar método en Odoo"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def search_customers(self, limit=10):
        """Buscar clientes existentes"""
        try:
            # Consulta básica que sabemos que funciona
            customer_ids = self.execute('res.partner', 'search', [])
            if customer_ids:
                # Tomar solo los primeros registros
                limited_ids = customer_ids[:limit] if len(customer_ids) > limit else customer_ids
                customers = self.execute('res.partner', 'read', limited_ids, ['name', 'email'])
                return customers
            else:
                print("No se encontraron partners")
                return []
                
        except Exception as e:
            print(f"Error buscando clientes: {e}")
            return []
    
    def search_products(self, limit=10):
        """Buscar productos existentes"""
        try:
            # Consulta básica de productos
            product_ids = self.execute('product.product', 'search', [])
            
            if product_ids:
                # Tomar solo los primeros registros
                limited_ids = product_ids[:limit] if len(product_ids) > limit else product_ids
                products = self.execute('product.product', 'read', limited_ids, 
                                      ['name', 'list_price', 'default_code'])
                return products
            else:
                print("No se encontraron productos")
                return []
                
        except Exception as e:
            print(f"Error buscando productos: {e}")
            # Intentar con product.template como alternativa
            try:
                print("Intentando buscar en product.template...")
                template_ids = self.execute('product.template', 'search', [])
                if template_ids:
                    limited_ids = template_ids[:limit] if len(template_ids) > limit else template_ids
                    templates = self.execute('product.template', 'read', limited_ids, 
                                           ['name', 'list_price', 'default_code'])
                    return templates
            except Exception as e2:
                print(f"Error en product.template: {e2}")
            return []
    
    def search_sale_order_types(self):
        """Buscar tipos de pedido de venta disponibles"""
        try:
            # Primero verificar si el modelo existe
            type_ids = self.execute('sale.order.type', 'search', [])
            
            if type_ids:
                # Obtener campos disponibles primero
                available_fields = self.get_model_fields('sale.order.type')
                print(f"🔍 Campos disponibles en sale.order.type: {len(available_fields)}")
                
                # Campos básicos que siempre deberían estar
                fields_to_read = ['name']
                
                # Agregar campos opcionales si existen
                optional_fields = {
                    'active': 'active',
                    'invoice_policy': 'invoice_policy', 
                    'auto_invoice': 'auto_invoice',
                    'auto_done': 'auto_done',
                    'pick_ship_policy_id': 'pick_ship_policy_id',
                    'sequence_id': 'sequence_id'
                }
                
                for field_key, field_name in optional_fields.items():
                    if field_name in available_fields:
                        fields_to_read.append(field_name)
                        print(f"  ✅ Campo {field_name} disponible")
                    else:
                        print(f"  ❌ Campo {field_name} no disponible")
                
                # Leer tipos con campos disponibles
                types = self.execute('sale.order.type', 'read', type_ids, fields_to_read)
                
                print(f"\n📋 Encontrados {len(types)} tipos de pedido:")
                return types
            else:
                print("No se encontraron tipos de pedido de venta")
                return []
                
        except Exception as e:
            # Si falla la consulta básica, el modelo no existe
            error_msg = str(e)
            if "does not exist" in error_msg or "model" in error_msg.lower():
                print(f"❌ El modelo 'sale.order.type' no existe en esta instalación")
                print(f"💡 Verifica que el módulo sale_order_type esté instalado correctamente")
            else:
                print(f"❌ Error accediendo al modelo: {e}")
            return []
    
    def get_sale_order_type_info(self, type_data):
        """Obtener información formateada de un tipo de pedido"""
        info = f"ID: {type_data['id']} - {type_data['name']}"
        
        # Estado activo
        if 'active' in type_data:
            active_status = "✅ Activo" if type_data.get('active', True) else "❌ Inactivo"
            info += f" | {active_status}"
        
        # Auto factura
        if 'auto_invoice' in type_data:
            auto_invoice = "🔄 Auto-factura" if type_data.get('auto_invoice', False) else "📋 Manual"
            info += f" | {auto_invoice}"
        
        # Política de facturación
        if 'invoice_policy' in type_data:
            invoice_policy = type_data.get('invoice_policy', 'N/A')
            info += f" | Política: {invoice_policy}"
            
        return info
    
    def create_sale_order_with_type(self, order_data, order_type_id=None):
        """Crear orden de venta con tipo específico"""
        try:
            # Preparar datos de la orden
            sale_order_data = {
                'partner_id': order_data['customer_id'],
                'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'order_line': []
            }
            
            # Agregar tipo de pedido si se especifica
            if order_type_id:
                sale_order_data['type_id'] = order_type_id
                print(f"📋 Asignando tipo de pedido ID: {order_type_id}")
            
            # Agregar líneas de productos
            for line in order_data['products']:
                order_line = (0, 0, {
                    'product_id': line['product_id'],
                    'product_uom_qty': line['quantity'],
                    'price_unit': line.get('price', 0)
                })
                sale_order_data['order_line'].append(order_line)
            
            # Crear la orden
            order_id = self.execute('sale.order', 'create', sale_order_data)
            print(f"✅ Orden de venta creada con ID: {order_id}")
            return order_id
            
        except Exception as e:
            print(f"❌ Error creando orden de venta: {e}")
            return None
    def create_sale_order(self, order_data):
        """Crear orden de venta (método legacy para compatibilidad)"""
        return self.create_sale_order_with_type(order_data, None)
    
    def confirm_sale_order(self, order_id):
        """Confirmar orden de venta (automáticamente creará factura si está configurado)"""
        try:
            # Obtener información de la orden antes de confirmar
            order_before = self.execute('sale.order', 'read', [order_id], 
                                      ['name', 'type_id', 'invoice_ids'])[0]
            
            type_info = ""
            if order_before.get('type_id'):
                type_name = order_before['type_id'][1]
                type_info = f" (Tipo: {type_name})"
                
            print(f"📋 Confirmando orden {order_before['name']}{type_info}")
            
            # Confirmar la orden
            self.execute('sale.order', 'action_confirm', [order_id])
            print(f"✅ Orden {order_id} confirmada exitosamente")
            
            # Verificar si se crearon facturas automáticamente
            order_after = self.execute('sale.order', 'read', [order_id], 
                                     ['invoice_ids', 'invoice_status'])[0]
            
            new_invoices = order_after.get('invoice_ids', [])
            old_invoices = order_before.get('invoice_ids', [])
            
            if len(new_invoices) > len(old_invoices):
                created_invoices = [inv for inv in new_invoices if inv not in old_invoices]
                print(f"🎉 ¡Factura(s) creada(s) automáticamente!")
                
                for inv_id in created_invoices:
                    try:
                        invoice = self.execute('account.move', 'read', [inv_id], 
                                             ['name', 'state', 'amount_total', 'invoice_origin'])
                        if invoice:
                            inv_data = invoice[0]
                            print(f"   📄 Factura: {inv_data['name']}")
                            print(f"      Estado: {inv_data['state']}")
                            print(f"      Origen: {inv_data.get('invoice_origin', 'N/A')}")
                            print(f"      Total: ${inv_data['amount_total']}")
                    except Exception:
                        print(f"   📄 Factura ID: {inv_id} (creada)")
                        
            else:
                print(f"ℹ️  Estado de facturación: {order_after.get('invoice_status', 'N/A')}")
                print(f"💡 Si configuraste facturación automática, verifica el tipo de pedido")
                
            return True
            
        except Exception as e:
            print(f"❌ Error confirmando orden: {e}")
            return False
    
    def create_invoice(self, order_id):
        """Crear factura desde orden de venta usando el flujo nativo de Odoo"""
        try:
            # Obtener la orden completa
            order = self.execute('sale.order', 'read', [order_id], 
                               ['state', 'partner_id', 'name', 'invoice_status'])[0]
            
            if order['state'] != 'sale':
                print("❌ La orden debe estar confirmada para crear factura")
                return None
            
            print(f"📋 Creando factura desde orden {order['name']} usando flujo nativo de Odoo...")
            
            # Método 1: Usar el wizard nativo de facturación de Odoo
            try:
                # Crear el wizard de advance payment con contexto correcto
                wizard_vals = {
                    'advance_payment_method': 'delivered',  # Facturar productos entregados
                    'deduct_down_payments': True,
                }
                
                # Crear el wizard con contexto de la orden activa
                wizard_id = self.execute('sale.advance.payment.inv', 'with_context', 
                                       {'active_ids': [order_id], 'active_model': 'sale.order'},
                                       'create', wizard_vals)
                
                if wizard_id:
                    # Ejecutar la creación de facturas
                    result = self.execute('sale.advance.payment.inv', 'create_invoices', [wizard_id])
                    
                    # Verificar si se creó la factura
                    updated_order = self.execute('sale.order', 'read', [order_id], ['invoice_ids'])[0]
                    if updated_order['invoice_ids']:
                        invoice_ids = updated_order['invoice_ids']
                        print(f"✅ Factura creada exitosamente desde pedido de venta")
                        print(f"   Factura(s) ID: {invoice_ids}")
                        
                        # Mostrar detalles de la factura creada
                        for inv_id in invoice_ids:
                            invoice = self.execute('account.move', 'read', [inv_id], 
                                                 ['name', 'state', 'amount_total', 'invoice_origin'])
                            if invoice:
                                inv_data = invoice[0]
                                print(f"   Número: {inv_data['name']}")
                                print(f"   Estado: {inv_data['state']}")
                                print(f"   Origen: {inv_data.get('invoice_origin', 'N/A')}")
                                print(f"   Total: ${inv_data['amount_total']}")
                        
                        return invoice_ids[0]  # Retornar el primer ID de factura
                    
            except Exception as e1:
                print(f"Método wizard con contexto falló: {e1}")
            
            # Método 2: Intentar directamente con el botón "Crear Factura"
            try:
                # Simular el clic en el botón "Crear Factura" desde la vista de formulario
                context = {
                    'active_model': 'sale.order',
                    'active_ids': [order_id],
                    'active_id': order_id,
                    'default_journal_id': False,
                }
                
                # Buscar si existe un wizard abierto
                wizard_model = 'sale.advance.payment.inv'
                wizard_vals = {
                    'advance_payment_method': 'delivered',
                }
                
                wizard_id = self.execute(wizard_model, 'create', wizard_vals)
                
                # Ejecutar con contexto específico
                self.execute(wizard_model, 'with_context', context, 'create_invoices', [wizard_id])
                
                # Verificar resultado
                updated_order = self.execute('sale.order', 'read', [order_id], ['invoice_ids'])[0]
                if updated_order['invoice_ids']:
                    print(f"✅ Factura creada con método directo")
                    return updated_order['invoice_ids'][0]
                    
            except Exception as e2:
                print(f"Método directo falló: {e2}")
            
            # Método 3: Usar action_invoice_create (si existe en versiones más antiguas)
            try:
                # Para versiones más antiguas de Odoo
                invoice_id = self.execute('sale.order', 'action_invoice_create', [order_id])
                if invoice_id:
                    print(f"✅ Factura creada con método legacy: {invoice_id}")
                    return invoice_id
                    
            except Exception as e3:
                print(f"Método legacy falló: {e3}")
            
            # Método 4: Llamar directamente el botón desde la interfaz
            try:
                # Simular llamada al botón específico
                result = self.execute('sale.order', 'action_quotation_send', [order_id])
                print(f"Resultado action_quotation_send: {result}")
                
            except Exception as e4:
                print(f"Método action falló: {e4}")
            
            print("❌ No se pudo crear la factura usando los métodos nativos de Odoo")
            print("💡 Intenta crear la factura manualmente desde la interfaz web de Odoo")
            print("   para verificar que la configuración del sistema permita la facturación")
            return None
                
        except Exception as e:
            print(f"❌ Error general creando factura: {e}")
            return None
    
    def get_model_fields(self, model_name):
        """Obtener campos disponibles de un modelo"""
        try:
            fields = self.execute(model_name, 'fields_get', [])
            return list(fields.keys())
        except Exception as e:
            print(f"Error obteniendo campos de {model_name}: {e}")
            return []
    
    def check_invoice_methods(self):
        """Verificar métodos disponibles para facturación"""
        try:
            print("\n🔍 MÉTODOS DE FACTURACIÓN DISPONIBLES:")
            print("-" * 50)
            
            # Obtener todos los métodos del modelo sale.order
            try:
                # Intentar obtener información del modelo
                model_info = self.execute('sale.order', 'fields_get', [])
                print(f"✅ Modelo sale.order accesible")
                
                # Verificar métodos específicos de facturación
                methods_to_check = [
                    'action_invoice_create',
                    '_create_invoices', 
                    'action_quotation_send',
                    'create_invoices',
                ]
                
                for method in methods_to_check:
                    try:
                        # Intentar llamar el método con una orden inexistente para ver si existe
                        self.execute('sale.order', method, [99999])
                    except Exception as e:
                        if "does not exist" in str(e):
                            print(f"❌ {method}: No disponible")
                        elif "not found" in str(e):
                            print(f"❌ {method}: No encontrado")
                        else:
                            print(f"✅ {method}: Disponible (error esperado con ID inválido)")
                
                # Verificar wizard de advance payment
                try:
                    wizard_info = self.execute('sale.advance.payment.inv', 'fields_get', [])
                    print(f"✅ Wizard sale.advance.payment.inv: Disponible")
                except Exception as e:
                    print(f"❌ Wizard sale.advance.payment.inv: No disponible - {e}")
                    
            except Exception as e:
                print(f"❌ Error verificando métodos: {e}")
                
            print("-" * 50)
            
        except Exception as e:
            print(f"Error en verificación: {e}")
    
    def diagnose_system(self):
        """Diagnosticar sistema Odoo"""
        print("\n🔍 DIAGNÓSTICO DEL SISTEMA:")
        print("-" * 40)
        
        # Verificar campos de res.partner
        partner_fields = self.get_model_fields('res.partner')
        print(f"Campos disponibles en res.partner: {len(partner_fields)}")
        customer_related = [f for f in partner_fields if 'customer' in f.lower() or 'client' in f.lower()]
        if customer_related:
            print(f"Campos relacionados con clientes: {customer_related}")
        
        # Verificar campos de product.product
        product_fields = self.get_model_fields('product.product')
        print(f"Campos disponibles en product.product: {len(product_fields)}")
        sale_related = [f for f in product_fields if 'sale' in f.lower()]
        if sale_related:
            print(f"Campos relacionados con ventas: {sale_related}")
            
        print("-" * 40)
    
    def get_order_info(self, order_id):
        """Obtener información de la orden"""
        try:
            order = self.execute('sale.order', 'read', [order_id], 
                               ['name', 'partner_id', 'state', 'amount_total', 'invoice_ids'])
            
            if order:
                order_data = order[0]
                print(f"  Número: {order_data['name']}")
                print(f"  Cliente: {order_data['partner_id'][1]}")
                print(f"  Estado: {order_data['state']}")
                print(f"  Total: ${order_data['amount_total']}")
                
                # Verificar facturas existentes
                if order_data.get('invoice_ids'):
                    print(f"  Facturas asociadas: {len(order_data['invoice_ids'])}")
                    for invoice_id in order_data['invoice_ids']:
                        try:
                            invoice = self.execute('account.move', 'read', [invoice_id], 
                                                 ['name', 'state', 'amount_total'])
                            if invoice:
                                inv_data = invoice[0]
                                print(f"    - Factura {inv_data['name']}: {inv_data['state']} - ${inv_data['amount_total']}")
                        except Exception:
                            print(f"    - Factura ID {invoice_id}: (no se pudo leer)")
                else:
                    print(f"  Facturas asociadas: 0")
                    
                return order_data
            return None
        except Exception as e:
            print(f"Error obteniendo info de orden: {e}")
            return None

def load_sample_data():
    """Cargar datos de ejemplo desde JSON"""
    try:
        with open('sample_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Archivo sample_data.json no encontrado")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error leyendo JSON: {e}")
        return None

def show_menu():
    """Mostrar menú principal"""
    print("\n" + "="*50)
    print("🛍️  ODOO CONSOLE - GESTIÓN DE VENTAS")
    print("="*50)
    print("1. Ver clientes disponibles")
    print("2. Ver productos disponibles")
    print("3. Ver tipos de pedido de venta")
    print("4. Crear orden de venta")
    print("5. Crear orden con tipo específico")
    print("6. Confirmar orden de venta")
    print("7. Crear factura desde orden (manual)")
    print("8. Ver información de orden")
    print("9. Diagnóstico del sistema")
    print("0. Salir")
    print("="*50)

def main():
    """Función principal"""
    print("🚀 Iniciando conexión con Odoo...")
    
    # Conectar con Odoo
    odoo = OdooConnector()
    if not odoo.connect():
        return
    
    # Cargar datos de ejemplo
    sample_data = load_sample_data()
    if not sample_data:
        return
    
    current_order_id = None
    
    while True:
        show_menu()
        choice = input("\n👉 Selecciona una opción: ").strip()
        
        if choice == '0':
            print("👋 ¡Hasta luego!")
            break
            
        elif choice == '1':
            print("\n📋 CLIENTES DISPONIBLES:")
            customers = odoo.search_customers()
            for customer in customers:
                print(f"  ID: {customer['id']} - {customer['name']} - {customer.get('email', 'Sin email')}")
                
        elif choice == '2':
            print("\n📦 PRODUCTOS DISPONIBLES:")
            products = odoo.search_products()
            for product in products:
                print(f"  ID: {product['id']} - {product['name']} - ${product['list_price']} - Código: {product.get('default_code', 'N/A')}")
                
        elif choice == '3':
            print("\n📋 TIPOS DE PEDIDO DE VENTA:")
            order_types = odoo.search_sale_order_types()
            if order_types:
                for order_type in order_types:
                    print(f"  {odoo.get_sale_order_type_info(order_type)}")
                    print()
            else:
                print("❌ No se encontraron tipos de pedido o módulo no instalado")
                
        elif choice == '4':
            print("\n🛒 CREAR ORDEN DE VENTA (SIN TIPO)")
            print("Usando datos de ejemplo del archivo JSON...")
            order_id = odoo.create_sale_order(sample_data['sale_order'])
            if order_id:
                current_order_id = order_id
                
        elif choice == '5':
            print("\n🛒 CREAR ORDEN DE VENTA CON TIPO")
            order_types = odoo.search_sale_order_types()
            if order_types:
                print("Tipos disponibles:")
                for i, order_type in enumerate(order_types, 1):
                    # Mostrar información básica para selección
                    name = order_type['name']
                    active = "✅" if order_type.get('active', True) else "❌"
                    auto = "🔄" if order_type.get('auto_invoice', False) else "📋"
                    print(f"  {i}. {name} {active} {auto}")
                
                try:
                    choice_type = input("\n👉 Selecciona un tipo (número): ").strip()
                    type_index = int(choice_type) - 1
                    if 0 <= type_index < len(order_types):
                        selected_type = order_types[type_index]
                        print(f"Creando orden con tipo: {selected_type['name']}")
                        order_id = odoo.create_sale_order_with_type(sample_data['sale_order'], 
                                                                  selected_type['id'])
                        if order_id:
                            current_order_id = order_id
                    else:
                        print("❌ Opción no válida")
                except (ValueError, IndexError):
                    print("❌ Entrada no válida")
            else:
                print("❌ No hay tipos de pedido disponibles")
                
        elif choice == '6':
            if current_order_id:
                print(f"\n✅ CONFIRMAR ORDEN {current_order_id}")
                odoo.confirm_sale_order(current_order_id)
            else:
                print("❌ No hay orden activa. Crea una orden primero.")
                
        elif choice == '7':
            if current_order_id:
                print(f"\n🧾 CREAR FACTURA PARA ORDEN {current_order_id}")
                invoice_id = odoo.create_invoice(current_order_id)
            else:
                print("❌ No hay orden activa. Crea una orden primero.")
                
        elif choice == '8':
            if current_order_id:
                print(f"\n📊 INFORMACIÓN DE ORDEN {current_order_id}")
                order_info = odoo.get_order_info(current_order_id)
            else:
                print("❌ No hay orden activa. Crea una orden primero.")
                
        elif choice == '9':
            print("\n🔍 EJECUTANDO DIAGNÓSTICO...")
            odoo.diagnose_system()
                
        else:
            print("❌ Opción no válida")
        
        input("\n⏸️  Presiona Enter para continuar...")

if __name__ == "__main__":
    main()