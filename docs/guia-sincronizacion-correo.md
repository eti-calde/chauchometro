# Guía de Sincronización de Correo

Esta guía explica cómo configurar tu cuenta de correo para que Chauchómetro pueda leer los emails de notificaciones bancarias.

## Gmail

### 1. Habilitar IMAP

1. Abre Gmail en tu navegador
2. Click en el ícono de configuración (⚙️) → **"Ver todos los ajustes"**
3. Ve a la pestaña **"Reenvío y correo POP/IMAP"**
4. En la sección IMAP, selecciona **"Habilitar IMAP"**
5. Click en **"Guardar cambios"**

### 2. Crear App Password

Gmail no permite autenticación con tu contraseña normal vía IMAP. Necesitas crear una "Contraseña de aplicación".

**Requisito previo:** Debes tener la verificación en dos pasos (2FA) activada en tu cuenta de Google.

1. Ve a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Si te pide iniciar sesión, ingresa tu contraseña de Google
3. En "Seleccionar app", elige **"Correo"**
4. En "Seleccionar dispositivo", elige **"Computadora Windows"** (o Mac según corresponda)
5. Click en **"Generar"**
6. Google te mostrará una contraseña de 16 caracteres (ejemplo: `abcd efgh ijkl mnop`)
7. **Copia esta contraseña** - la necesitarás en el siguiente paso

> **Importante:** Esta contraseña solo se muestra una vez. Si la pierdes, deberás generar una nueva.

### 3. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus credenciales:

```bash
cd backend
cp .env.example .env
```

Edita el archivo `.env`:

```env
EMAIL_ADDRESS=tu_email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
EMAIL_PROVIDER=gmail
```

> **Nota:** La App Password va **sin espacios**.

---

## Outlook / Hotmail

### 1. Verificar que IMAP está habilitado

Por defecto, IMAP está habilitado en Outlook.com. Para verificar:

1. Ve a [outlook.com](https://outlook.com) e inicia sesión
2. Click en configuración (⚙️) → **"Ver toda la configuración de Outlook"**
3. Ve a **Correo → Sincronizar correo electrónico**
4. Verifica que **"Permitir que los dispositivos y las aplicaciones usen POP"** esté activado

### 2. Configurar variables de entorno

```env
EMAIL_ADDRESS=tu_email@outlook.com
EMAIL_PASSWORD=tu_contraseña
EMAIL_PROVIDER=outlook
```

> **Nota:** Si tienes 2FA activado en Microsoft, necesitarás crear una contraseña de aplicación en [account.microsoft.com/security](https://account.microsoft.com/security).

---

## Probar la conexión

Una vez configurado, puedes probar que todo funciona ejecutando:

```bash
cd backend
pip install -r requirements.txt  # si no lo has hecho antes
python -m test.parsers.test_scraping
```

Este script se conectará a tu correo, buscará emails de notificaciones bancarias y mostrará las transacciones encontradas.

### Salida esperada

Si tienes emails del Banco de Chile, verás algo como:

```
Conectando a tu_email@gmail.com...
Conexión exitosa!
Buscando emails de enviodigital@bancochile.cl...
Encontrados: 15 emails

Transacción 1:
  Tipo: COMPRA
  Monto: $25.990
  Comercio: SUPERMERCADO JUMBO
  Fecha: 2024-03-15
```

---

## Solución de problemas

### Error: "Authentication failed"

- Verifica que la App Password esté correcta (sin espacios)
- Asegúrate de que IMAP esté habilitado
- Verifica que el `EMAIL_PROVIDER` sea correcto (`gmail` u `outlook`)

### Error: "Connection refused"

- Verifica tu conexión a internet
- Algunos firewalls corporativos bloquean conexiones IMAP

### No encuentra emails

- Verifica que tengas emails de `enviodigital@bancochile.cl` en tu bandeja
- Revisa que no estén en la carpeta de spam

---

## Seguridad

- **Nunca compartas** tu archivo `.env` ni lo subas a repositorios públicos
- El archivo `.env` ya está incluido en `.gitignore`
- Considera usar un correo dedicado solo para notificaciones bancarias
- Puedes revocar la App Password en cualquier momento desde la configuración de tu cuenta Google/Microsoft
