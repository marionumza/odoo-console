# 🛍️ Odoo Console - Gestión de Ventas desde la Consola

Script en Python para operar con Odoo desde la línea de comandos, permitiendo crear órdenes de venta, confirmarlas y generar facturas automáticamente usando tipos de pedido personalizados.

## 📋 Características

- ✅ **Conexión segura** a Odoo vía XML-RPC
- ✅ **Consulta de clientes** y productos existentes
- ✅ **Creación de órdenes de venta** con o sin tipos específicos
- ✅ **Confirmación automática** de pedidos
- ✅ **Facturación automática** usando tipos de pedido configurados
- ✅ **Diagnóstico del sistema** para verificar compatibilidad
- ✅ **Gestión de tipos de pedido** del módulo `sale_order_type`

## 🔧 Requisitos

### Software requerido:
- **Python 3.7+**
- **Odoo 12.0+** (cualquier versión moderna)
- **Acceso XML-RPC** habilitado en Odoo

### Módulos de Odoo requeridos:
- **`sale`** (Ventas) - Módulo base incluido en Odoo
- **`sale_order_type`** - Módulo adicional para tipos de pedido ⚠️ **IMPORTANTE**

## 📦 Instalación

### 1. Clonar/Descargar archivos
```bash
# Descargar los siguientes archivos:
# - odoo_console.py
# - .env
# - sample_data.json
# - requirements.txt
```

### 2. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 3. Configurar conexión
Edita el archivo `.env` con los datos de tu servidor Odoo:

```bash
ODOO_URL=http://tu-servidor-odoo:8069
ODOO_DB=nombre_de_tu_base_de_datos
ODOO_USERNAME=tu_usuario
ODOO_PASSWORD=tu_contraseña
```

**Ejemplo:**
```bash
ODOO_URL=https://tuempresa.odoo.com
ODOO_DB=production
ODOO_USERNAME=admin
ODOO_PASSWORD=admin123
```

## 🔌 Configuración de Odoo

### 1. Instalar módulo `sale_order_type`

El módulo **`sale_order_type`** es fundamental para la funcionalidad de facturación automática.

#### Opción A: OCA (Odoo Community Association)
```bash
# Si usas OCA, instalar desde:
# https://github.com/OCA/sale-workflow/tree/16.0/sale_order_type
```

#### Opción B: Odoo Apps Store
1. Ve a **Apps** en tu instancia de Odoo
2. Busca "**Sale Order Type**" o "**Tipos de Pedido de Venta**"
3. Instala el módulo

#### Opción C: Instalación manual
1. Descarga el módulo `sale_order_type`
2. Colócalo en tu directorio de addons
3. Actualiza la lista de aplicaciones
4. Instala el módulo

### 2. Configurar tipos de pedido para facturación automática

Una vez instalado el módulo:

1. **Ve a:** `Ventas > Configuración > Tipos de Pedido`

2. **Crear/Editar un tipo de pedido:**
   - **Nombre:** `Facturación Automática` (o el nombre que prefieras)
   - **Activo:** ✅ Marcado
   - **Auto Invoice:** ✅ Marcado (campo clave para facturación automática)
   - **Política de facturación:** Según tu necesidad

3. **Campos importantes a configurar:**
   ```
   ✅ active = True
   ✅ auto_invoice = True  # Campo clave para facturación automática
   📋 invoice_policy = 'order' o 'delivery' (según tu flujo)
   ```

### 3. Verificar permisos de usuario

El usuario configurado en `.env` debe tener:
- ✅ **Permisos de Ventas** (crear/editar órdenes)
- ✅ **Permisos de Facturación** (crear facturas)
- ✅ **Acceso XML-RPC** (habilitado por defecto)

## 🚀 Modo de Uso

### Ejecución del script
```bash
python odoo_console.py
```

### Menú principal
```
🛍️  ODOO CONSOLE - GESTIÓN DE VENTAS
==================================================
1. Ver clientes disponibles
2. Ver productos disponibles
3. Ver tipos de pedido de venta
4. Crear orden de venta
5. Crear orden con tipo específico
6. Confirmar orden de venta
7. Crear factura desde orden (manual)
8. Ver información de orden
9. Diagnóstico del sistema
0. Salir
```

### Flujo recomendado para facturación automática:

#### **Paso 1: Verificar datos disponibles**
```bash
👉 Selecciona una opción: 1  # Ver clientes
👉 Selecciona una opción: 2  # Ver productos
👉 Selecciona una opción: 3  # Ver tipos de pedido
```

#### **Paso 2: Actualizar datos de ejemplo**
Edita `sample_data.json` con IDs reales de tu sistema:
```json
{
  "sale_order": {
    "customer_id": 42,  # ID real de cliente
    "products": [
      {
        "product_id": 15,  # ID real de producto
        "quantity": 2,
        "price": 100.00
      }
    ]
  }
}
```

#### **Paso 3: Crear orden con tipo de facturación automática**
```bash
👉 Selecciona una opción: 5  # Crear orden con tipo específico
👉 Selecciona un tipo (número): 1  # Elegir tipo con auto-facturación
```

#### **Paso 4: Confirmar orden (automáticamente crea factura)**
```bash
👉 Selecciona una opción: 6  # Confirmar orden
# 🎉 ¡La factura se creará automáticamente!
```

#### **Paso 5: Verificar resultado**
```bash
👉 Selecciona una opción: 8  # Ver información completa
```

## 📁 Estructura de archivos

```
odoo-console/
├── odoo_console.py      # Script principal
├── .env                 # Configuración de conexión
├── sample_data.json     # Datos de ejemplo
├── requirements.txt     # Dependencias Python
└── README.md           # Esta documentación
```

## 🔍 Diagnóstico y resolución de problemas

### Verificar instalación del módulo
```bash
👉 Selecciona una opción: 3  # Ver tipos de pedido
```

Si muestra:
- ✅ **Lista de tipos:** Módulo instalado correctamente
- ❌ **Error de modelo:** Módulo no instalado

### Verificar configuración
```bash
👉 Selecciona una opción: 9  # Diagnóstico del sistema
```

### Problemas comunes:

#### 1. **Error de conexión**
```
❌ Error de conexión: [Errno 111] Connection refused
```
**Solución:** Verificar URL y que Odoo esté ejecutándose

#### 2. **Error de autenticación**
```
❌ Error de autenticación
```
**Solución:** Verificar username, password y base de datos

#### 3. **Módulo no encontrado**
```
❌ El modelo 'sale.order.type' no existe
```
**Solución:** Instalar módulo `sale_order_type`

#### 4. **Campos no disponibles**
```
❌ Campo auto_invoice no disponible
```
**Solución:** Verificar versión del módulo o configurar manualmente

## 📋 Ejemplo de flujo completo

### Configuración inicial en Odoo:
1. Instalar `sale_order_type`
2. Crear tipo "Auto-Factura" con `auto_invoice = True`
3. Verificar permisos de usuario

### Uso del script:
```bash
python odoo_console.py

# 1. Ver clientes y productos
👉 1 → Copiar ID de cliente (ej: 42)
👉 2 → Copiar ID de producto (ej: 15)

# 2. Actualizar sample_data.json con IDs reales

# 3. Ver tipos de pedido
👉 3 → Identificar tipo con 🔄 (auto-factura)

# 4. Crear orden con tipo automático
👉 5 → Seleccionar tipo con auto-factura

# 5. Confirmar orden
👉 6 → ¡Factura creada automáticamente!

# 6. Verificar resultado
👉 8 → Ver orden y facturas asociadas
```

## 🎯 Resultado esperado

Al confirmar una orden con tipo de auto-facturación:

```
✅ Orden 37 confirmada exitosamente
🎉 ¡Factura(s) creada(s) automáticamente!
   📄 Factura: INV/2024/0001
      Estado: draft
      Origen: S00002
      Total: $250.00
```

## 🛠️ Personalización

### Agregar nuevos campos:
Edita la función `search_sale_order_types()` para incluir campos específicos de tu instalación.

### Modificar datos de ejemplo:
Edita `sample_data.json` para incluir productos y clientes de tu sistema.

### Agregar nuevas funcionalidades:
El script está diseñado para ser extensible. Puedes agregar nuevas opciones al menú principal.

Este script demuestra que es posible **operar Odoo completamente desde la consola**, automatizando el flujo completo de:
- **Creación de órdenes** → **Confirmación** → **Facturación automática**

Este script demuestra que es posible operar Odoo completamente desde la consola, automatizando el flujo completo de:

Creación de órdenes → Confirmación → Facturación automática

Usando la funcionalidad nativa de Odoo con tipos de pedido personalizados, manteniendo toda la trazabilidad y relaciones correctas entre documentos.