# 💸 Chauchómetro 💸

> La app open source que te ayuda a no estar pato nunca más

Chauchómetro es una aplicación de finanzas personales que automatiza el tracking de gastos mediante el scraping inteligente de correos electrónicos bancarios. Diseñada por y para chilenos que quieren tener sus lucas ordenadas.

## 🎯 Features Principales

### Core (MVP)
- 📧 **Scraping Automático de Emails**: Detecta y procesa automáticamente correos de pagos bancarios
- 🏷️ **Categorización Inteligente**: Solicita categorizar cada movimiento para un tracking preciso
- 📊 **Dashboard de Gastos**: Visualización clara de gastos e ingresos por categoría
- 🔔 **Notificaciones en Tiempo Real**: Alerta inmediata cuando detecta un nuevo gasto
- 🏦 **Multi-banco**: Soporte para los principales bancos chilenos

### Próximamente
- 💸 **Presupuestos**: Define límites mensuales por categoría con alertas
- 📈 **Análisis Predictivo**: Proyecciones basadas en patrones históricos
- 🔄 **Detección de Suscripciones**: Identifica gastos recurrentes automáticamente
- 📱 **PWA**: Acceso móvil para categorizar sobre la marcha
- 📋 **Exportación**: Descarga tus datos en Excel/CSV
- 🔐 **Encriptación E2E**: Tus datos financieros, siempre seguros

## 🛠️ Stack Tecnológico

### Frontend
- **Next.js** + **TypeScript**: Framework React con SSR
- **TailwindCSS**: Estilos utility-first
- **Recharts**: Gráficos y visualizaciones
- **IndexedDB** (via Dexie.js): Almacenamiento local para modo offline
- **React Query**: Manejo de estado del servidor

### Backend
- **FastAPI**: API moderna y rápida
- **PostgreSQL**: Base de datos principal
- **Redis**: Caché y colas de trabajo
- **Celery**: Procesamiento asíncrono de emails
- **SQLAlchemy**: ORM

### Scraping & Parsing
- **imaplib**: Conexión IMAP a servidores de correo
- **BeautifulSoup4**: Parsing de HTML de emails
- **Parsers modulares**: Sistema extensible para agregar bancos

## 🚀 Instalación Rápida
(pendiente)

## 🏦 Bancos Soportados

- 🚧 Banco de Chile (en progreso)
- 🚧 BancoEstado
- 🚧 Santander
- 🚧 BCI
- 🚧 Scotiabank
- 🚧 Banco Falabella 

## 🤝 Contribuir

¡Chauchómetro es open source y necesitamos tu ayuda!

### Cómo contribuir
1. Fork el proyecto
2. Crea tu Feature Branch (`git checkout -b feature/NuevoBanco`)
3. Commit tus cambios (`git commit -m 'Agrega soporte para Banco X'`)
4. Push a la Branch (`git push origin feature/NuevoBanco`)
5. Abre un Pull Request

**¡¡USAMOS [Conventional Commits](https://www.conventionalcommits.org/) en español !!**

por ejemplo:

```
feat(parser): agregar soporte para Banco Scotiabank.
- punteo detallando lo que se hizo
- más detalle.
cierra issue [BANK-013] #25
```
donde "BANK-013" es el código de la issue y 25 es el ID de la issue.

### Áreas donde necesitamos ayuda
- 🏦 Agregar más parsers de bancos
- 🎨 Mejorar UI/UX
- 🧪 Tests
- 📚 Documentación
- 🌎 Internacionalización

## 🔒 Seguridad

- **Self-hosting**: Tus datos nunca salen de tu servidor
- **Encriptación**: Credenciales de email encriptadas con AES-256
- **Procesamiento local**: Todo el análisis ocurre en tu máquina
- **Sin tracking**: Cero analytics, cero telemetría

## 📄 Licencia

MIT License.

---

**¿Problemas? ¿Sugerencias?** Abre un [issue](https://github.com/tu-usuario/chauchometro/issues)

**¿Te sirvió?** Deja tu ⭐ en el repo
Hecho con ❤️ y harto ☕ en Chile 🇨🇱