# Documento de diseño: Observatorio de Turismo Sostenible, Tikal y Flores (Petén)

**CC3066 Data Science | UVG | Semestre II 2026 | Laboratorio 10 | Grupo 2**
Integrantes: Iris Ayala 23960, Jonathan Díaz 23837 y Anggie Quezada 23643

> Estado: **borrador del avance** (22 de octubre de 2026). Las secciones 4.1, 4.3, 4.4, 4.5 y 4.6
> están completas para el avance. La 4.2 tiene la propuesta de visualizaciones y se afinará en la
> entrega final.

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
| M | Migración (Labs 1 y 2) | `Base_Migracion_2009-2026jun.xlsx` | ene 2009 a jun 2026 | Ingresos internacionales al país. La asignación la indica como **serie estacional para pronosticar ene y feb 2026**, justo los meses que faltan en telefonía. Incluye 4 fronteras de Petén |
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
5. **Telefonía, cobertura corta:** solo hay 10 meses y faltan enero y febrero de 2026. Los
   meses en común con el AIMM son apenas 6 (sep a dic 2025, mar y abr 2026). Además el **93 % de
   los visitantes detectados son guatemaltecos**, así que la cifra está dominada por turismo
   interno. Los valores son estimaciones expandidas (con decimales), no conteos exactos.
6. **Vuelos ≠ pasajeros:** las operaciones (aterrizajes y despegues) y los pasajeros son unidades
   distintas y **nunca se suman ni se grafican en el mismo eje**.
7. **Pasajeros ≠ turistas:** el AIMM incluye residentes que viajan y personal. Un boleto de Tikal
   no equivale a un turista único (una persona puede entrar dos veces). Las fuentes se comparan por
   **tendencia**, no por cantidad absoluta.
8. **Modelos predictivos:** se reutilizan los de los Labs 1 y 2, que se entrenaron con la demanda
   internacional **nacional** (migración). Se presentan como contexto del mercado que alimenta a
   Petén y como la estimación de enero y febrero de 2026, no como pronóstico de Tikal.

---

## 4.4 Preguntas de gestión (exploratorias)

| # | Pregunta de gestión | Decisión que apoya | Fuente | Sección |
|---|---|---|---|---|
| P1 | ¿Cuántos visitantes recibe Tikal, cómo se recuperó frente a 2019 y qué proporción son nacionales y extranjeros? | Fijar metas de visitación y orientar la promoción al mercado que crece o se rezaga | 1 | Tikal |
| P2 | ¿En qué meses se concentra la visita a Tikal y qué tan marcada es la temporada alta? | **Sostenibilidad:** gestionar la capacidad de carga del parque, planificar personal y servicios, y promover la temporada baja | 1 | Tikal |
| P3 | ¿Qué **porcentaje de los visitantes que están en Petén compra boleto a Tikal**, y las tres fuentes cuentan la misma historia mes a mes? | Medir qué tanto del turismo de Petén capta el parque, detectar demanda que no llega a Tikal (oportunidad para Flores y El Remate) y saber cuándo un cambio es confiable | 1, 2, 3 | Triangulación |
| P4 | ¿Cuánto pesa cada aerolínea en los pasajeros del AIMM, cómo se reconstruye 2023 y qué tan dependiente es Petén de pocos operadores? | Negociar rutas y frecuencias y medir el riesgo si un operador reduce su servicio | 2a, 2b, 2c | Conectividad |
| P5 | ¿La ocupación hotelera de Petén acompaña la temporada alta de Tikal? ¿En qué meses hay presión sobre la capacidad instalada y en cuáles sobra capacidad? | **Sostenibilidad:** detectar saturación (más de 85 % de ocupación), planificar la oferta de hospedaje y promover los meses con capacidad libre | H1, H2, 1 | Hospedaje |
| P6 | ¿Cuánta demanda internacional estiman los modelos para enero y febrero de 2026 y qué tan confiables son? | Cubrir con una estimación los meses sin dato de telefonía, conociendo su margen de error | M (Labs 1 y 2) | Predicciones |

**Preguntas descartadas:** el perfil y la satisfacción del visitante y la percepción de los
residentes corresponden a otro enfoque de Petén según la asignación. También se descartan los
totales de gasto (la encuesta no se puede expandir) y las causas de los cambios (los datos muestran
patrones, no causas).

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
- Resultados de **3 modelos de los Labs 1 y 2**: Prophet, ARIMA y Holt-Winters (con seasonal
  naive como referencia), con sus errores sobre el periodo de prueba (abril 2021 a junio 2026)
  explicados en lenguaje sencillo.
- Textos cortos que dicen qué muestra cada gráfica, para qué sirve y cuáles son sus límites.
  Mensajes claros cuando una selección no tiene datos (por ejemplo, AIMM por segmento en 2023).

**No incluye:**

- Modelos nuevos ni reentrenamiento en la app. Las predicciones se leen de archivos generados con
  el código de los Labs 1 y 2.
  *(Pendiente de consultar con el profesor: si se permite aplicar la misma receta de los Labs 1 y
  2 a la serie de Tikal, se agregaría como extra en la entrega final.)*
- Pronósticos de Tikal o del AIMM.
- Perfil y satisfacción del visitante y percepción de residentes (otro enfoque de Petén). Quedan
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
4. **Hecho frente a estimación:** el dato observado es una línea continua gris oscuro y las
   estimaciones son líneas punteadas.
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
| Primario / **selección** | `#0B5563` | 8.4:1 | Barra de navegación, pestaña activa y **el elemento que el usuario seleccionó** (año, modelo, aerolínea). Azul petróleo, asociado a agua y selva, coherente con turismo sostenible |
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
| Migración, fronteras de Petén | `#C2185B` magenta | 5.9:1 | Frontera |

**Modelos (Predicciones):** para no agregar 3 colores más, los modelos se distinguen por **tipo de
línea** (Prophet `- - -`, ARIMA `· · ·`, Holt-Winters `-·-·`) y por una **etiqueta al final de cada
línea**. Se usa el patrón **foco + contexto**: el modelo seleccionado se dibuja en el color de
selección `#0B5563` y los demás en gris claro `#B8C0C8`. El dato observado siempre es `#1F2933`
continuo.

**Escalas continuas:**

- **Secuencial** (mapa de calor de estacionalidad): un solo tono de azul petróleo, de `#E6F2F3`
  (pocos visitantes) a `#0B5563` (muchos). Más oscuro significa más, y se entiende sin leyenda.
- **Años como categoría ordenada** (ocupación hotelera, V8): tonos del mismo azul petróleo, más
  claro para el año más antiguo y más oscuro para el más reciente. El orden temporal se lee por
  intensidad sin inventar colores nuevos. El umbral de saturación (85 %) es una línea punteada gris.
- **Errores del modelo** (V12): barras en el color de selección que suben si el modelo
  sobreestima y bajan si subestima. La dirección la da la posición respecto a 0, no un color
  adicional.
- **Periodos especiales:** el cierre del parque (abril a septiembre de 2020) se marca con una franja
  gris `#E4E7EB` y su etiqueta. Los meses sin dato se dejan en blanco con tramado, nunca como 0.

### Tipografía

- **Inter** (Google Fonts, licencia abierta): diseñada para pantallas, legible en tamaños pequeños y
  con **números tabulares** (los dígitos tienen el mismo ancho), lo que facilita comparar cifras.
  Respaldo: `system-ui, sans-serif`.
- **Jerarquía:** título de página 28 px semibold, título de gráfica 18 px semibold, subtítulo 14 px
  en texto secundario, ejes y leyendas 12 px como mínimo.
- Números con separador de miles y abreviados en tarjetas (por ejemplo 401 mil).

### Bosquejo de la interfaz

Estructura común a todas las páginas:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ▣ Observatorio · Tikal y Flores   [Resumen][Tikal][Triangulación]        │
│                                   [Conectividad][Hospedaje][Predicciones]│  ← barra #0B5563
│                                   [Acerca de]                            │
├───────────────┬──────────────────────────────────────────────────────────┤
│ FILTROS       │  Título de la página                                     │
│ (según página)│  "¿Qué responde esta página?" (texto corto)              │
│               │ ┌──────────┐┌──────────┐┌──────────┐┌──────────┐         │
│ Periodo       │ │ KPI      ││ KPI      ││ KPI      ││ KPI      │         │  ← tarjetas (complementarias)
│ [2017 ─ 2026] │ └──────────┘└──────────┘└──────────┘└──────────┘         │
│ Segmento      │ ┌───────────────────────────┐┌─────────────────────────┐ │
│ ☑Nacionales   │ │ Gráfica A                 ││ Gráfica B (enlazada a A)│ │
│ ☑Extranjeros  │ │ Qué muestra / para qué    ││ cambia al hacer clic    │ │
│ ☑Otros        │ │                           ││ en A                    │ │
│               │ └───────────────────────────┘└─────────────────────────┘ │
│ Detalle       │ ┌──────────────────────────────────────────────────────┐ │
│ (•)Año ( )Trim│ │ Gráfica C                                            │ │
│ ( )Mes        │ └──────────────────────────────────────────────────────┘ │
│ [Restablecer] │  ⚠ Nota de limitación cuando aplica                      │
└───────────────┴──────────────────────────────────────────────────────────┘
```

**Página "Tikal"** (P1, P2), la que se implementa en el avance:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ V1 Visitantes a Tikal por segmento (líneas · detalle Año/Trim/Mes)      │
│    ▒▒ parque cerrado 2020                                               │
│    → clic en un año ──────────────────┐                                 │
├───────────────────────────────────────┼─────────────────────────────────┤
│ V2 Estacionalidad mes × año           ▼ el año elegido se resalta       │
│    mapa de calor (oscuro = más visitantes)                              │
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
| **Resumen** | Panorama | Tarjetas (visitantes a Tikal en el último año, % contra 2019, mes pico, pasajeros AIMM) y guía de uso |
| **Tikal** | P1, P2 | V1, V2, V3 |
| **Triangulación** | P3 | V4, V5 |
| **Conectividad** | P4 | V6, V7 |
| **Hospedaje** | P5 | V8, V9 |
| **Predicciones** | P6 | V10, V11, V12 |
| **Acerca de** | n/a | Fuentes, glosario (índice base 100, MAE, RMSE, estacionalidad, triangulación), limitaciones |

**Principios de HCI y UX aplicados:**

- **Visión general primero, después zoom y filtros, y detalle a pedido** (Shneiderman): tarjetas
  → gráfica general → clic para el detalle.
- **Filtros fijos a la izquierda** y botón "Restablecer" para volver al inicio (control y
  libertad del usuario).
- **Retroalimentación inmediata:** lo seleccionado se resalta en `#0B5563` y aparece un texto como
  "Mostrando: 2019 · clic de nuevo para quitar".
- **Carga cognitiva baja:** 2 o 3 gráficas por página, cada una con un subtítulo de una línea.
- **Prevención de errores:** si una selección no tiene datos, aparece un mensaje con la razón en
  lugar de una gráfica vacía.
- **Consistencia:** los mismos colores, tipografía y lugar de los controles en todas las páginas.
- **Lenguaje de negocio:** "error promedio del modelo (visitantes)" en lugar de "RMSE", con el
  término técnico entre paréntesis y en el glosario.

---

## 4.2 Visualizaciones propuestas y tipo de gráfica

Se proponen 12 visualizaciones interactivas (el mínimo es 8). Las marcadas ★ son las 8 prioritarias.
Tarjetas, controles, textos y la tabla de modelos son complementarios y **no** se cuentan.

| # | Visualización | Pág. | Tipo | Por qué ese tipo | Interacción |
|---|---|---|---|---|---|
| ★V1 | Visitantes mensuales a Tikal por segmento | Tikal | Líneas | El tiempo es continuo. La línea muestra tendencia, estacionalidad y el cierre de 2020 | Detalle Año/Trim/Mes, zoom, mostrar u ocultar segmentos, **clic en un año → V2 y V3** |
| ★V2 | Estacionalidad mes × año | Tikal | Mapa de calor | Dos ejes ordinales (mes, año) y una cantidad: el color secuencial deja ver de un vistazo qué meses son temporada alta | Resalta el año elegido en V1, filtra por segmento |
| ★V3 | Mezcla nacional/extranjero por mes | Tikal | Barras apiladas al 100 % | Compara proporciones de pocas categorías | Muestra el año elegido en V1 |
| ★V4 | Las 3 fuentes en una escala común | Triang. | Líneas de índice (base 100 = promedio de los meses en común) | Las fuentes tienen escalas muy distintas (miles contra cientos de miles). El índice las pone en el mismo eje para comparar la **forma**. Los meses sin dato quedan como huecos, no como ceros | Elegir fuentes, **clic en un mes → V5** |
| ★V5 | % de visitantes en Petén que compra boleto a Tikal | Triang. | Barras agrupadas por mes (nacionales / extranjeros) | Es el indicador clave de la asignación. Las barras comparan bien una proporción mes a mes y entre dos segmentos | Resalta el mes elegido en V4 y muestra el detalle por polígono |
| ★V6 | Pasajeros AIMM por aerolínea y año (con 2023 reconstruido) | Conect. | Treemap año → aerolínea | Muestra jerarquía y concentración (T.A.G. y Aviateca suman más del 95 %) y permite **bajar y subir de nivel** | Clic para profundizar o regresar. **Clic en una aerolínea → V7** |
| V7 | Pasajeros y operaciones mensuales del operador elegido | Conect. | Dos paneles de líneas alineados (eje X compartido, eje Y propio) | Las dos medidas tienen unidades distintas: en paneles separados se comparan en el tiempo **sin mezclar vuelos con pasajeros** | Cambia según la aerolínea elegida en V6 |
| ★V8 | Ocupación hotelera mensual de Petén, un año por línea | Hosp. | Gráfico estacional (eje X = mes, una línea por año) con banda de referencia en 85 % | Al superponer los años se ve si la temporada alta se repite y en qué meses hay saturación o capacidad libre | Mostrar u ocultar años. **Clic en un mes → V9** |
| V9 | Capacidad instalada frente a demanda del mes elegido | Hosp. | Barras apiladas de habitaciones por tipo (hotel, hospedaje, pensión), con marca de habitaciones ocupadas estimadas (ocupación × habitaciones) | Traduce un porcentaje abstracto en habitaciones, una unidad que el directivo entiende | Cambia según el mes y año elegidos en V8 |
| ★V10 | Observado frente a predicción de 3 modelos | Pred. | Línea observada + líneas punteadas | Hecho y estimación en el mismo eje temporal. Se marcan ene y feb 2026 (los meses sin telefonía) | Elegir serie (Total, Vía Aérea, frontera). Resalta el modelo elegido en V11 |
| V11 | Error promedio por modelo | Pred. | Barras horizontales | Comparar magnitudes de pocos modelos: barra más corta = mejor | **Clic en un modelo → V10 y V12 lo resaltan** |
| V12 | Errores del modelo mes a mes | Pred. | Barras divergentes | Muestra cuándo el modelo sobreestima o subestima | Cambia según el modelo elegido en V11 |

**Enlaces entre gráficas (requisito 3.2):** V1 → V2 y V3 · V4 → V5 · V6 → V7 · V8 → V9 ·
V11 → V10 y V12.

**Más y menos detalle (requisito 1.4):** Año/Trim/Mes en V1, treemap año → aerolínea en V6,
zoom temporal en V1, V4 y V10, y clic en un año para ver sus meses.

---

## 4.3 Herramienta seleccionada: Python + Plotly Dash

| Criterio | **Plotly Dash** | Streamlit | R Shiny | Panel / Voilà |
|---|---|---|---|---|
| Gráficas enlazadas por clic o selección | **Nativo** (`clickData`, `selectedData` en callbacks) | Limitado: vuelve a ejecutar todo el script en cada interacción | Nativo | Posible, más configuración |
| Control del diseño (CSS, layout, tipografía) | **Total** (HTML + CSS propio) | Bajo: el diseño es fijo | Alto | Medio |
| Reutilizar el código de los Labs 1 y 2 (pandas, statsmodels, Prophet) | **Sí, mismo lenguaje** | Sí | No, habría que portar a R | Sí |
| Rendimiento | Solo recalcula la gráfica afectada | Recalcula todo en cada clic | Bueno | Bueno |
| Licencia | MIT, gratis | Apache 2.0, gratis | GPL, gratis | BSD, gratis |
| Despliegue gratuito | Render, Hugging Face Spaces | Streamlit Cloud | shinyapps.io (limitado) | HF Spaces |

**Por qué Dash:** el tablero depende de **5 grupos de gráficas enlazadas** y de **cambiar el nivel
de detalle**. En Dash cada clic o selección dispara un *callback* que actualiza solo las gráficas
afectadas, así que los enlaces son precisos y rápidos. Da control total del CSS, necesario para
aplicar la paleta, la tipografía y el diseño profesional que pide el público directivo. Como los
Labs 1 y 2 están en Python, las predicciones se reutilizan sin traducir código. Plotly aporta zoom,
*hover*, treemap con drill-down y selección por arrastre sin desarrollo adicional.

**Arquitectura prevista:**

```
lab10-ds/
├── app.py                   # punto de entrada Dash: layout y navegación
├── pages/                   # una página por pestaña
├── assets/style.css         # paleta y tipografía (Dash lo carga automáticamente)
├── src/
│   ├── datos.py             # carga y limpieza de las fuentes
│   └── tema.py              # constantes de color y plantilla Plotly
├── scripts/
│   └── exportar_predicciones.py   # genera una vez las predicciones de los Labs 1-2
├── datos/                   # fuentes originales (xlsx)
└── docs/
```

---

## 4.6 Planificación de tareas

> Responsables por confirmar con el grupo. El historial del repositorio debe mostrar aportes de los
> tres integrantes.

| # | Tarea | Responsable | Fecha de terminación | Estado |
|---|---|---|---|---|
| 1 | Preguntas de gestión, alcance, paleta y justificación | Anggie Quezada | Jue 22-oct | En revisión |
| 2 | Bosquejo de interfaz, navegación y elección de herramienta | Anggie Quezada | Jue 22-oct | En revisión |
| 3 | Estructura del proyecto Dash, carga y limpieza de boletos de Tikal | Anggie Quezada | Jue 22-oct | Pendiente |
| 4 | V1 y V2 funcionales y enlazadas (avance) | Anggie Quezada | Jue 22-oct 17:20 | Pendiente |
| 5 | Entrega del avance (PDF + repositorio) | Anggie Quezada | Jue 22-oct 17:20 | Pendiente |
| 6 | V3 y cierre de la página Tikal | Iris Ayala | Vie 23-oct | Pendiente |
| 7 | Limpieza de AIMM (3 archivos, reconstrucción 2023), telefonía y ocupación hotelera, índice base 100 | Jonathan Díaz | Vie 23-oct | Pendiente |
| 8 | Página Triangulación (V4, V5) | Jonathan Díaz | Sáb 24-oct | Pendiente |
| 9 | Página Conectividad (V6, V7) | Iris Ayala | Sáb 24-oct | Pendiente |
| 10 | Página Hospedaje con ocupación y oferta hotelera (V8, V9) | Iris Ayala | Sáb 24-oct | Pendiente |
| 11 | Exportar predicciones de los Labs 1 y 2 y página Predicciones (V10 a V12) | Jonathan Díaz | Sáb 24-oct | Pendiente |
| 12 | Páginas Resumen y Acerca de (glosario, limitaciones) | Anggie Quezada | Dom 25-oct | Pendiente |
| 13 | Pruebas de uso, mensajes sin datos y ajustes de UX | Todo el grupo | Dom 25-oct | Pendiente |
| 14 | Documento de diseño final en PDF | Anggie Quezada | Dom 25-oct | Pendiente |
| 15 | Entrega final | Todo el grupo | Dom 25-oct | Pendiente |
