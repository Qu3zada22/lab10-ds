# Documento de diseño: Observatorio de Turismo Sostenible, Tikal y Flores (Petén)

**CC3066 Data Science | UVG | Semestre II 2026 | Laboratorio 10 | Grupo 2**
Integrantes: Iris Ayala 23960, Jonathan Díaz 23837 y Anggie Quezada 23643

> **Avance, 22 de octubre de 2026.** Contiene las preguntas de gestión y el alcance del tablero, la
> paleta de colores y su justificación, la planificación de tareas y responsables, el bosquejo de
> la interfaz y la navegación, y la herramienta elegida con su justificación. La sección 4.2 tiene
> la propuesta de visualizaciones y se completará en la entrega final.
>
> **Nota sobre modelos:** por indicación del catedrático, este laboratorio es solo un tablero
> descriptivo. No se incluyen modelos predictivos ni de clasificación; esos quedan para el
> Proyecto 3.

---

## 0. Contexto y fuentes de datos

El tablero es parte del **observatorio de turismo sostenible** del proyecto. Al Grupo 2 le
corresponde **Tikal y Flores (Petén)** con el enfoque de **triangulación de 3 fuentes
independientes**: boletos de ingreso a Tikal, operaciones y pasajeros del Aeropuerto
Internacional Mundo Maya (AIMM) y telefonía. Va dirigido a directivos y tomadores de decisiones
del sector turístico que no necesariamente tienen formación estadística.

**¿Qué es triangular?** Ninguna fuente mide "todos los turistas de Petén". Cada una mide una parte:
quién compró boleto en Tikal, quién voló al AIMM, qué teléfonos estuvieron en la zona. Si las tres
**suben y bajan al mismo tiempo**, se puede confiar más en que el cambio en la demanda es real y no
un error de una sola fuente.

| # | Fuente | Archivo | Periodo | Qué mide |
|---|---|---|---|---|
| 1 | Boletos a Tikal | `Visitantes_Tikal_2017-2026.xlsx` | ene 2017 a ago 2026, mensual | Ingresos al Parque Nacional Tikal: nacionales, extranjeros y otros (exonerados) |
| 2a | AIMM, pasajeros por segmento | `AIMM_Consolidado_2022-2025.xlsx` | 2022, 2024, 2025, mensual | Entradas y salidas por segmento: doméstico, internacional y privado |
| 2b | AIMM, pasajeros por aerolínea | `AIMM_Aerolineas_2023-2026.xlsx` | ene 2023 a abr 2026, mensual | Pasajeros por aerolínea y flujo. **Cubre el 2023 que falta en 2a** |
| 2c | AIMM, operaciones | `AIMM_Operaciones_Aeronauticas_2022-2026.xlsx` | ene 2022 a abr 2026, mensual | Aterrizajes y despegues por operador |
| 3 | Telefonía (movilidad) | `BD_moviidad_mensual.xlsx`, hoja `Peten` | sep 2025 a ago 2026, mensual (**sin ene y feb 2026**) | Visitantes estimados por telefonía en 3 polígonos (Mundo Maya Aeropuerto, Isla de Flores, El Remate), por país, estancia (menor o mayor a 1 día), días-persona y permanencia promedio |
| H1 | Ocupación hotelera | `indice_ocupacion_mensual_2023_2025_1.csv` | ene 2023 a dic 2025, mensual | Índice de ocupación por departamento (se filtra Petén). Archivo común obligatorio |
| H2 | Oferta hotelera | `oferta_hotelera_2022_2026.csv` | 4.º trim. 2022 a 1.er trim. 2026, cortes anuales | Establecimientos, habitaciones y plazas cama por tipo (hotel, hospedaje, pensión). Petén tiene unas 4,000 habitaciones. Archivo común obligatorio |

**Fuentes de apoyo (opcionales, fuera del alcance principal):** encuesta al visitante de Petén 2025
(500 casos), encuesta a residentes 2025 (513 casos en Petén, solo tabulada), `BD_COMPLEMENTARIA`
(Parquet) y boletines PDF de ocupación. Según la asignación, el perfil del visitante y la
percepción de la comunidad corresponden a otro enfoque de Petén. Se agregarán solo si sobra
tiempo.

**Limitaciones que el tablero debe comunicar siempre que aplique:**

1. **Tikal, abril a septiembre de 2020:** vale 0 porque el parque estuvo cerrado por la pandemia.
   Es un dato real, no un faltante. Enero de 2017 también vale 0 y se tratará como sin dato.
2. **AIMM 2023:** no existe en la base consolidada por segmento (la fuente dice que no hay
   información). Se completa el total con la base por aerolínea. Los totales de 2024 coinciden en
   ambas bases (365,422), lo que da confianza.
3. **Periodos distintos:** Tikal llega hasta agosto de 2026 y el AIMM hasta abril de 2026. Las
   comparaciones entre fuentes usan solo los **meses en común**.
4. **Hospedaje:** la ocupación es un índice de **todo el departamento de Petén**, no solo de
   Flores, y no tiene datos de 2026. La oferta hotelera es un corte por año, no mensual.
5. **Telefonía, cobertura corta:** solo hay 10 meses y faltan enero y febrero de 2026. Los meses en
   común con el AIMM son apenas 6 (sep a dic 2025, mar y abr 2026). Además el **93 % de los
   visitantes detectados son guatemaltecos**, así que la cifra está dominada por turismo interno.
   Los valores son estimaciones expandidas (con decimales), no conteos exactos.
6. **Vuelos ≠ pasajeros:** las operaciones (aterrizajes y despegues) y los pasajeros son unidades
   distintas y **nunca se suman ni se grafican en el mismo eje**.
7. **Pasajeros ≠ turistas:** el AIMM incluye residentes que viajan y personal. Un boleto de Tikal
   no equivale a un turista único (una persona puede entrar dos veces). Las fuentes se comparan por
   **tendencia**, no por cantidad absoluta.

---

## 4.4 Preguntas de gestión (exploratorias)

| # | Pregunta de gestión | Decisión que apoya | Fuente | Sección |
|---|---|---|---|---|
| P1 | ¿Cuántos visitantes recibe Tikal, cómo se recuperó frente a 2019 y qué proporción son nacionales y extranjeros? | Fijar metas de visitación y orientar la promoción al mercado que crece o se rezaga | 1 | Tikal |
| P2 | ¿En qué meses se concentra la visita a Tikal y qué tan marcada es la temporada alta? | **Sostenibilidad:** gestionar la capacidad de carga del parque, planificar personal y servicios, y promover la temporada baja | 1 | Tikal |
| P3 | ¿Qué **porcentaje de los visitantes que están en Petén compra boleto a Tikal**, y las tres fuentes cuentan la misma historia mes a mes? | Medir qué tanto del turismo de Petén capta el parque, detectar demanda que no llega a Tikal (oportunidad para Flores y El Remate) y saber cuándo un cambio es confiable | 1, 2, 3 | Triangulación |
| P4 | ¿Cuánto pesa cada aerolínea en los pasajeros del AIMM, cómo se reconstruye 2023 y qué tan dependiente es Petén de pocos operadores? | Negociar rutas y frecuencias y medir el riesgo si un operador reduce su servicio | 2a, 2b, 2c | Conectividad |
| P5 | ¿La ocupación hotelera de Petén acompaña la temporada alta de Tikal? ¿En qué meses hay presión sobre la capacidad instalada y en cuáles sobra capacidad? | **Sostenibilidad:** detectar saturación (más de 85 % de ocupación), planificar la oferta de hospedaje y promover los meses con capacidad libre | H1, H2, 1 | Hospedaje |

**Preguntas descartadas:** pronósticos de demanda (por indicación del catedrático, los modelos
quedan para el Proyecto 3); el perfil y la satisfacción del visitante y la percepción de los
residentes (corresponden a otro enfoque de Petén según la asignación); los totales de gasto (la
encuesta no se puede expandir) y las causas de los cambios (los datos muestran patrones, no causas).

---

## 4.5 Alcance del tablero

**Incluye:**

- Visitación mensual a Tikal (2017 a 2026) por segmento, con más o menos detalle: año → trimestre
  → mes.
- Comparación de las tres fuentes en una escala común (índice base 100) para el periodo en que
  todas tienen datos, y el indicador clave **% de visitantes en Petén que compra boleto a Tikal**
  (boletos ÷ visitantes por telefonía), separado en nacionales y extranjeros.
- Conectividad aérea del AIMM: **reconstrucción de 2023** con la base por aerolínea, cuota de cada
  aerolínea y operaciones por operador, sin mezclar vuelos con pasajeros.
- Hospedaje en Petén: ocupación mensual 2023 a 2025 frente a la capacidad instalada (habitaciones
  por tipo de alojamiento).
- Textos cortos que dicen qué muestra cada gráfica, para qué sirve y cuáles son sus límites.
  Mensajes claros cuando una selección no tiene datos (por ejemplo, AIMM por segmento en 2023).

**No incluye:**

- Modelos predictivos o de clasificación ni pronósticos (quedan para el Proyecto 3).
- Perfil y satisfacción del visitante ni percepción de residentes (otro enfoque de Petén). Quedan
  como extra opcional.
- Explicaciones causales.
- Carga de datos nuevos por parte del usuario y gestión de usuarios.

---

## 4.1 Diseño visual

### Paleta de colores

**Criterios:**

1. **Significado fijo en toda la app:** cada color representa una sola cosa. Por ejemplo, el verde
   siempre es "boletos de Tikal" y el azul petróleo siempre es "lo que seleccionaste".
2. **Apta para daltonismo:** los colores categóricos parten de **Okabe-Ito** (diseñada para
   deuteranopía y protanopía), oscurecidos para cumplir contraste. No se usa la combinación
   rojo-verde para comparar.
3. **Contraste WCAG 2.1:** texto ≥ 4.5:1 y elementos gráficos ≥ 3:1. Los valores se calcularon con
   la fórmula de luminancia relativa de WCAG.
4. **Dato medido frente a dato estimado:** los conteos (boletos, pasajeros) van con línea continua. La telefonía, que es una estimación expandida, va con línea punteada.
5. **Interfaz neutra:** grises y blanco en la interfaz. El color saturado se reserva para los datos
   y la selección.
6. **Máximo 4 colores por gráfica**, para no saturar la memoria de trabajo del usuario.

**Interfaz**

| Rol | Color | Contraste sobre blanco | Uso |
|---|---|---|---|
| Fondo de página | `#F5F7F8` | n/a | Fondo general |
| Tarjetas | `#FFFFFF` | n/a | Contenedor de cada gráfica |
| Texto principal | `#1F2933` | 14.8:1 | Títulos, valores, etiquetas |
| Texto secundario | `#52606D` | 6.5:1 | Subtítulos, notas, ejes |
| Primario / **selección** | `#0B5563` | 8.4:1 | Barra de navegación, pestaña activa y **el elemento que el usuario seleccionó** (año, mes, aerolínea). Azul petróleo, asociado a agua y selva, coherente con turismo sostenible |
| Contexto | `#B8C0C8` | n/a | Elementos no seleccionados cuando hay una selección activa (foco + contexto) |
| Aviso | fondo `#FFF4E5`, ícono `#9A6700` | 4.9:1 | Mensajes de limitación ("sin dato", "parque cerrado") |

**Datos: segmento de visitante** (Tikal y telefonía)

| Categoría | Color | Contraste |
|---|---|---|
| Nacionales | `#0072B2` azul | 5.2:1 |
| Extranjeros | `#C25400` bermellón | 4.6:1 |
| Otros / exonerados | `#7B8794` gris medio | 3.7:1 |

**Datos: fuente** (Triangulación y Conectividad)

| Fuente | Color | Contraste | Asociación |
|---|---|---|---|
| Boletos Tikal | `#00826A` verde selva | 4.8:1 | El parque, la selva |
| AIMM (pasajeros y vuelos) | `#7B4FB0` violeta | 5.9:1 | Aire |
| Telefonía | `#9A6700` ámbar | 4.9:1 | Señal |

Dentro de una misma fuente (por ejemplo, las aerolíneas del AIMM) no se agregan
colores nuevos: se usan tonos del color de la fuente y el elemento seleccionado pasa al color de
selección.

**Escalas continuas:**

- **Secuencial** (mapa de calor de estacionalidad): un solo tono de azul petróleo, de `#E6F2F3`
  (pocos visitantes) a `#0B5563` (muchos). Más oscuro significa más, y se entiende sin leyenda.
- **Años como categoría ordenada** (ocupación hotelera, V8): tonos del mismo azul petróleo, más
  claro para el año más antiguo y más oscuro para el más reciente. El orden temporal se lee por
  intensidad sin inventar colores nuevos. El umbral de saturación (85 %) es una línea punteada gris.
- **Periodos especiales:** el cierre del parque (abril a septiembre de 2020) se marca con una franja
  gris `#E4E7EB` y su etiqueta. Los meses sin dato se dejan en blanco, nunca como 0.

### Tipografía

- **Inter** (Google Fonts, licencia abierta): diseñada para pantallas, legible en tamaños pequeños y
  con **números tabulares** (los dígitos tienen el mismo ancho), lo que facilita comparar cifras.
  Respaldo: `system-ui, sans-serif`.
- **Jerarquía:** título de página 28 px semibold, título de gráfica 18 px semibold, subtítulo 14 px
  en texto secundario, ejes y leyendas 12 px como mínimo.
- Números con separador de miles (401,060) y porcentajes con un decimal (+17.0 %).

### Bosquejo de la interfaz

Estructura común a todas las páginas:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Observatorio de Turismo Sostenible  [Tikal][Triangulación]               │
│ Tikal y Flores · Petén              [Conectividad][Hospedaje]            │  ← barra #0B5563
├───────────────┬──────────────────────────────────────────────────────────┤
│ FILTROS       │  Título de la página                                     │
│ (según página)│  "¿Qué responde esta página?" (texto corto)              │
│               │ ┌──────────┐┌──────────┐┌──────────┐┌──────────┐         │
│ Segmento      │ │ KPI      ││ KPI      ││ KPI      ││ KPI      │         │  ← tarjetas (complementarias)
│ ☑Nacionales   │ └──────────┘└──────────┘└──────────┘└──────────┘         │
│ ☑Extranjeros  │  Mostrando: 2019 · resaltado en ambas  [Quitar selección]│  ← estado de la selección
│ ☑Otros        │ ┌──────────────────────────────────────────────────────┐ │
│               │ │ Gráfica A   ¿Qué muestra? / ¿Para qué sirve?         │ │
│ Periodo       │ │             → clic en un elemento                    │ │
│ [2017 ─ 2026] │ └──────────────────────────────────────────────────────┘ │
│               │ ┌──────────────────────────────────────────────────────┐ │
│ Nivel detalle │ │ Gráfica B (enlazada a A, se actualiza con el clic)   │ │
│ ( )Año        │ └──────────────────────────────────────────────────────┘ │
│ ( )Trimestre  │  ⚠ Sobre los datos: limitaciones que aplican             │
│ (•)Mes        │                                                          │
│ [Restablecer] │                                                          │
└───────────────┴──────────────────────────────────────────────────────────┘
```

**Página "Tikal"** (P1, P2):

```
┌─────────────────────────────────────────────────────────────────────────┐
│ V1 Visitantes a Tikal por segmento (líneas · detalle Año/Trim/Mes)      │
│    ▒▒ parque cerrado 2020   ○ = periodo incompleto                      │
│    → clic en un año ──────────────────┐                                 │
├───────────────────────────────────────┼─────────────────────────────────┤
│ V2 Estacionalidad mes × año           ▼ el año elegido se enmarca y     │
│    mapa de calor (oscuro = más)         los demás se aclaran            │
│    → clic en una fila resalta el año en V1                              │
├─────────────────────────────────────────────────────────────────────────┤
│ V3 Nacionales frente a extranjeros por mes del año elegido (100 %)      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Página "Triangulación"** (P3):

```
┌─────────────────────────────────────────────────────────────────────────┐
│ V4 Índice base 100 de las 3 fuentes (líneas, mismo eje)                 │
│    → clic en un mes ───────────────────┐                                │
├────────────────────────────────────────┼────────────────────────────────┤
│ V5 % de visitantes en Petén con boleto ▼ el mes elegido se resalta y    │
│    a Tikal (barras por mes, nac./ext.)   se detalla por polígono        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Navegación

Las pestañas van de lo general a lo particular, en el orden de las preguntas:

| Pestaña | Pregunta | Contenido |
|---|---|---|
| **Tikal** | P1, P2 | V1, V2, V3 |
| **Triangulación** | P3 | V4, V5 |
| **Conectividad** | P4 | V6, V7 |
| **Hospedaje** | P5 | V8, V9 |

**Principios de HCI y UX aplicados:**

- **Visión general primero, después zoom y filtros, y detalle a pedido** (Shneiderman): tarjetas
  → gráfica general → clic para el detalle.
- **Filtros fijos a la izquierda** y botón "Restablecer" para volver al inicio (control y
  libertad del usuario).
- **Retroalimentación inmediata:** lo seleccionado se resalta en `#0B5563` y aparece una barra de
  estado ("Mostrando: 2019 · resaltado en ambas gráficas") con el botón "Quitar selección".
- **Carga cognitiva baja:** 2 o 3 gráficas por página, cada una con un subtítulo que dice qué
  muestra y para qué sirve.
- **Prevención de errores:** si una selección no tiene datos, aparece un mensaje con la razón en
  lugar de una gráfica vacía.
- **Consistencia:** los mismos colores, tipografía y lugar de los controles en todas las páginas.
- **Lenguaje de negocio:** "boletos vendidos", "habitaciones ocupadas", "índice (100 = promedio)",
  con los términos técnicos explicados en el subtítulo de cada gráfica.
- **Hechos frente a interpretaciones:** las gráficas muestran lo observado. Los avisos dicen qué no
  se puede concluir (por ejemplo, que un cambio tenga una causa concreta).

---

## 4.2 Visualizaciones propuestas y tipo de gráfica

Se proponen 9 visualizaciones interactivas (el mínimo es 8). Tarjetas, controles y textos son
complementarios y **no** se cuentan.

| # | Visualización | Pág. | Tipo | Por qué ese tipo | Interacción |
|---|---|---|---|---|---|
| V1 | Visitantes mensuales a Tikal por segmento | Tikal | Líneas | El tiempo es continuo. La línea muestra tendencia, estacionalidad y el cierre de 2020 | Detalle Año/Trim/Mes, zoom, mostrar u ocultar segmentos, **clic en un año → V2 y V3** |
| V2 | Estacionalidad mes × año | Tikal | Mapa de calor | Dos ejes ordinales (mes, año) y una cantidad: el color secuencial deja ver de un vistazo qué meses son temporada alta | Filtra por segmento. **Clic en un año → V1** (enlace en ambos sentidos) |
| V3 | Mezcla nacional/extranjero por mes | Tikal | Barras apiladas al 100 % | Compara proporciones de pocas categorías | Muestra el año elegido en V1 o V2 |
| V4 | Las 3 fuentes en una escala común | Triang. | Líneas de índice (base 100 = promedio de los meses en común) | Las fuentes tienen escalas muy distintas (miles contra cientos de miles). El índice las pone en el mismo eje para comparar la **forma**. Los meses sin dato quedan como huecos, no como ceros | Elegir fuentes, **clic en un mes → V5** |
| V5 | % de visitantes en Petén que compra boleto a Tikal | Triang. | Barras agrupadas por mes (nacionales / extranjeros) | Es el indicador clave de la asignación. Las barras comparan bien una proporción mes a mes y entre dos segmentos | Resalta el mes elegido en V4 y muestra el detalle por polígono |
| V6 | Pasajeros AIMM por aerolínea y año (con 2023 reconstruido) | Conect. | Treemap año → aerolínea | Muestra jerarquía y concentración (T.A.G. y Aviateca suman más del 95 %) y permite **bajar y subir de nivel** | Clic para profundizar o regresar. **Clic en una aerolínea → V7** |
| V7 | Pasajeros y operaciones mensuales del operador elegido | Conect. | Dos paneles de líneas alineados (eje X compartido, eje Y propio) | Las dos medidas tienen unidades distintas: en paneles separados se comparan en el tiempo **sin mezclar vuelos con pasajeros** | Cambia según la aerolínea elegida en V6 |
| V8 | Ocupación hotelera mensual de Petén, un año por línea | Hosp. | Gráfico estacional (eje X = mes, una línea por año) con línea de referencia en 85 % | Al superponer los años se ve si la temporada alta se repite y en qué meses hay saturación o capacidad libre | Mostrar u ocultar años. **Clic en un mes → V9** |
| V9 | Capacidad instalada frente a demanda del mes elegido | Hosp. | Barras apiladas de habitaciones por tipo (hotel, hospedaje, pensión), con marca de habitaciones ocupadas estimadas (ocupación × habitaciones) | Traduce un porcentaje abstracto en habitaciones, una unidad que el directivo entiende | Cambia según el mes y año elegidos en V8 |

**Enlaces entre gráficas (requisito 3.2):** V1 ↔ V2 y V3 · V4 → V5 · V6 → V7 · V8 → V9.

**Más y menos detalle (requisito 1.4):** Año/Trimestre/Mes en V1, treemap año → aerolínea en V6,
zoom temporal en V1 y V4, y clic en un año para ver sus meses.

**Selección de gráficas (requisito 3.3):** cada página muestra solo las gráficas de su pregunta. El
usuario elige qué series ver (segmentos, fuentes, años) desde la leyenda y los filtros.

---

## 4.3 Herramienta seleccionada: Python + Plotly Dash

| Criterio | **Plotly Dash** | Streamlit | R Shiny | Panel / Voilà |
|---|---|---|---|---|
| Gráficas enlazadas por clic o selección | **Nativo** (`clickData`, `selectedData` en callbacks) | Limitado: vuelve a ejecutar todo el script en cada interacción | Nativo | Posible, más configuración |
| Control del diseño (CSS, layout, tipografía) | **Total** (HTML + CSS propio) | Bajo: el diseño es fijo | Alto | Medio |
| Lenguaje que el grupo ya usa (Python, pandas) | **Sí** | Sí | No, habría que aprender R | Sí |
| Rendimiento | Solo recalcula la gráfica afectada | Recalcula todo en cada clic | Bueno | Bueno |
| Aplicación de varias páginas | Nativo (`use_pages`) | Sí | Sí | Limitado |
| Licencia | MIT, gratis | Apache 2.0, gratis | GPL, gratis | BSD, gratis |
| Despliegue gratuito | Render, Hugging Face Spaces | Streamlit Cloud | shinyapps.io (limitado) | HF Spaces |

**Por qué Dash:** el tablero depende de **5 grupos de gráficas enlazadas** y de **cambiar el nivel
de detalle**. En Dash cada clic o selección dispara un *callback* que actualiza solo las gráficas
afectadas, así que los enlaces son precisos y rápidos. Da control total del CSS, necesario para
aplicar la paleta, la tipografía y el diseño profesional que pide el público directivo. El grupo ya
trabaja en Python y pandas, así que la limpieza de las fuentes se hace en el mismo lenguaje que la
app. Plotly aporta zoom, *hover*, treemap con drill-down y selección sin desarrollo adicional.

**Arquitectura:**

```
lab10-ds/
├── app.py                   # punto de entrada: layout, barra y navegación
├── pages/                   # una página por pestaña (tikal, conectividad y hospedaje implementadas)
├── assets/style.css         # paleta y tipografía (Dash lo carga automáticamente)
├── src/
│   ├── datos.py             # carga y limpieza de las fuentes
│   ├── tema.py              # constantes de color y plantilla de Plotly
│   └── componentes.py       # tarjetas, avisos y mensajes "sin datos" reutilizables
├── datos/                   # fuentes originales de INGUAT (no se versionan)
└── docs/
```

---

## 4.6 Planificación de tareas

> El historial del repositorio debe mostrar aportes de los tres integrantes.

| # | Tarea | Responsable | Estado |
|---|---|---|---|
| 1 | Preguntas de gestión, alcance, paleta y justificación | Anggie Quezada | Completado |
| 2 | Bosquejo de interfaz, navegación y elección de herramienta | Anggie Quezada | Completado |
| 3 | Estructura del proyecto Dash, carga y limpieza de boletos de Tikal | Anggie Quezada | Completado |
| 4 | Página Tikal: V1 y V2 enlazadas | Anggie Quezada | Completado |
| 5 | Página Tikal: V3 | Iris Ayala | Completado |
| 6 | Página Conectividad: V6 y V7 (cargadores del AIMM, 2023 reconstruido) | Iris Ayala | Completado |
| 7 | Página Hospedaje: V8 y V9 (cargadores de ocupación y oferta hotelera) | Iris Ayala | Completado |
| 8 | Cargador de telefonía en `src/datos.py` e índice base 100 | Jonathan Díaz | **Pendiente** |
| 9 | Página Triangulación: V4 y V5 | Jonathan Díaz | **Pendiente** |
| 10 | Documento de diseño final en PDF (revisar que 4.1 a 4.6 coincidan con lo construido) | Jonathan Díaz | **Pendiente** |
| 11 | Entrega: el PDF y el link del repositorio, con el historial de los tres integrantes | Jonathan Díaz | **Pendiente** |

Hay 7 visualizaciones listas (V1 a V3, V6 a V9). El mínimo es 8, así que la página de Triangulación
(V4 y V5) es lo único que falta para cumplirlo y deja el tablero en 9.

**Qué se entrega (según el enunciado del lab):** el documento de diseño en PDF y el link del repositorio
donde se versionó el código. El repositorio debe ser privado, con los catedráticos y auxiliares como
colaboradores, y sin la carpeta `datos/`.

### Archivos de la carpeta `datos/`

La carpeta va en la raíz del proyecto y no se versiona (los datos son confidenciales). Se descargan de
la carpeta "Datos Inguat". El link de descarga está en la entrega del Proyecto 3 en Canvas.

| Archivo | Lo usa |
|---|---|
| `Visitantes_Tikal_2017-2026.xlsx` | Tikal, Triangulación |
| `AIMM_Consolidado_2022-2025.xlsx` | Conectividad, Triangulación |
| `AIMM_Aerolineas_2023-2026.xlsx` | Conectividad, Triangulación |
| `AIMM_Operaciones_Aeronauticas_2022-2026.xlsx` | Conectividad |
| `indice_ocupacion_mensual_2023_2025_1.csv` | Hospedaje |
| `oferta_hotelera_2022_2026.csv` | Hospedaje |
| `BD_moviidad_mensual.xlsx` (hoja `Peten`) | Triangulación |

### Cómo se programa una página nueva

1. Crear el cargador de datos en `src/datos.py`, con el mismo estilo que `tikal()` o `aimm_aerolineas()`:
   formato largo, columnas `fecha`, `anio` y `mes`, `lru_cache`, y los meses sin dato como `NaN`, nunca 0.
2. Crear `pages/<nombre>.py` con `dash.register_page(...)`, copiando la estructura de
   `pages/conectividad.py` o `pages/hospedaje.py`: tarjetas con `kpi()`, un `dcc.Store` para la
   selección, `tarjeta_grafica()`, `figura_vacia()` para los mensajes de "sin datos" y `aviso()` con las
   limitaciones.
3. Tomar los colores de `src/tema.py`, sin códigos sueltos.
4. Borrar la entrada de la página en `PENDIENTES` de `app.py`.

### Qué lleva la página pendiente

- **Triangulación:** V4 es el índice base 100 de las tres fuentes en un mismo eje (promedio de los meses
  en común). V5 es el % de visitantes en Petén que compra boleto a Tikal, separado en nacionales y
  extranjeros. Un clic en un mes de V4 lo resalta en V5. Se reutilizan `tikal()` y `aimm_pasajeros_total()`.
  Solo se comparan los meses en común, y los meses sin dato quedan en blanco, nunca en 0.
