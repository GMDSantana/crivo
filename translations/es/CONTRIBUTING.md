<p align="center">
Traducciones <br>
<a href=https://github.com/GMDSantana/crivo/tree/master/CONTRIBUTING.md>🇬🇧 EN</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/es/CONTRIBUTING.md>🇪🇸 ES</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/pt-br/CONTRIBUTING.md>🇧🇷 PT-BR</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/zh-cn/CONTRIBUTING.md>🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Contribuyendo al Crivo

¡Hola! 👋

Entonces, ¿tienes interés en contribuir al Crivo? 🤔 ¡Eso es una gran noticia!

Ya seas una persona con experiencia o alguien que está comenzando, tus contribuciones son más que bienvenidas. Tal vez te preguntes: "¿Son suficientes mis habilidades de programación?" La respuesta es: ¡por supuesto! Todo el mundo tiene algo valioso que aportar, y estaremos encantados de colaborar independientemente de tu nivel de experiencia. Si estás leyendo este documento, ya estás por delante de muchas personas—¡no todo el mundo aprende a contribuir a proyectos en GitHub! 😉

Aquí tienes algunas maneras de contribuir al Crivo:

- Añadir nuevas capacidades de filtrado o mejoras 🛠️
- Mejorar las funcionalidades de web scraping 🌐
- Crear o mejorar la documentación (¡estaremos inmensamente agradecidos!) 📖
- Corregir errores reportados a través de issues en GitHub 🐛
- Refactorizar el código para hacerlo más limpio o eficiente ✨

¿Suena complicado? ¡No te preocupes! Este documento te guiará paso a paso. Tus contribuciones no solo mejorarán el Crivo, sino que también garantizarán un lugar en la lista de contribuidores—¡y nuestra gratitud eterna! 🙏

Hemos creado una página de discusiones en GitHub para que puedas hablar con los mantenedores, resolver dudas o sugerir funcionalidades. Alternativamente, puedes abrir un issue directamente en el repositorio de GitHub.

---

## Cómo Contribuir

¡Hay muchas maneras de hacer que Crivo sea aún mejor! A continuación, te mostramos algunas áreas específicas en las que sería genial contar con tu ayuda.

### 1. Añadir Nuevas Funcionalidades 🛠️

Crivo destaca por su versatilidad. Si tienes una idea para una nueva funcionalidad—como un filtro de alcance adicional, una lógica de análisis más robusta o un nuevo formato de salida—¡adelante, impleméntala!

Para empezar:
- Haz un fork del repositorio.
- Crea una nueva rama para tu funcionalidad:
  ```bash
  git checkout -b feature/your-feature-name
  ```
- Implementa la funcionalidad.
- Añade pruebas para asegurarte de que todo funciona correctamente.
- Envía un pull request para revisión.

---

### 2. Mejorar el Web Scraping 🌐

Las capacidades de web scraping son una parte esencial de Crivo. Si tienes experiencia en scraping o detectas algo que se puede mejorar, tus contribuciones serán invaluables. Por ejemplo:

- Mejorar la forma en que se resuelven los enlaces relativos.
- Añadir manejo de casos como HTML malformado o estructuras de URL inusuales.

---

### 3. Crear o Mejorar la Documentación 📖

La documentación es el pilar de cualquier proyecto exitoso. Una buena documentación asegura que otras personas puedan usar y contribuir al Crivo de manera efectiva.

Maneras en las que puedes ayudar:

- Añadir docstrings en el código.
- Mejorar la documentación existente (e.g., README.md, este archivo).
- Traducir la documentación a otros idiomas.
- Escribir tutoriales o guías de uso.

Una buena documentación es tan valiosa como las contribuciones en el código, y estaremos inmensamente agradecidos por tu ayuda.

---

### 4. Corregir Errores 🐛

Seguimos los problemas conocidos en la sección de Issues de GitHub. Si te gustan los desafíos:

- Escoge un error que te interese.
- Comenta en el issue para informarnos que estás trabajando en él.
- Envía tu corrección como un pull request.

Corregir errores es una excelente forma de familiarizarte con el código mientras haces una contribución significativa.

---

### 5. Refactorizar el Código ✨

No todo el código de Crivo es perfecto, y siempre hay espacio para mejoras. Si identificas oportunidades para:

- Eliminar código duplicado.
- Hacer el código más modular o fácil de leer.
- Asegurarte de que el código siga los estándares PEP8 de Python.

¡Adelante! Tus mejoras harán que Crivo sea más fácil de mantener para todos.

---

## Escribir Pruebas

Al añadir una nueva funcionalidad o corregir un error, recomendamos que escribas pruebas para asegurarte de que todo funcione como se espera. Crivo utiliza pytest para sus pruebas.

### Cómo Escribir Pruebas

1. Ve al directorio tests/ en el repositorio.
2. Crea un nuevo archivo de prueba o añade tus pruebas a uno ya existente.
3. Escribe tus funciones de prueba siguiendo la convención de nomenclatura test_<funcionalidad_o_error>().

### Ejecutar Pruebas

Para ejecutar las pruebas, utiliza el comando pytest en la terminal:

```bash
pytest
```

Esto ejecutará todas las pruebas en el directorio tests/ y mostrará los resultados.

---

## Enviando Tus Contribuciones

1. Una vez que hayas hecho tus cambios, envíalos al fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Abre un pull request en el repositorio principal.

Revisaremos tu contribución, proporcionaremos comentarios si es necesario y haremos el merge tan pronto como todo esté listo.

---

## ¡Gracias! 🙏

Contribuir a proyectos de código abierto es una experiencia enriquecedora, y estamos encantados de que hayas decidido contribuir al Crivo. Tu esfuerzo, tiempo y conocimientos son profundamente valorados. ¡Estamos deseando ver tus contribuciones!

¡Felices contribuciones! 💻 
