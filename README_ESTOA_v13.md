# ESTOA v13 - Motor mareográfico nacional
Ingestión geométrica de PUB 3009 2026 para 7 puertos patrón y transformación a las 8 estaciones de corriente con relación mareográfica exacta.
El backend /conditions/at entrega marea numérica cuando existe corrección de altura y conserva solo horarios PM/BM en EVENT_TIMES_ONLY.
Ahora y Momento consumen el mismo objeto tide.

Corrección QA importante: la referencia antigua de Kirke para 04-10-2026 estaba asociada a una columna equivocada de la tabla trimestral.
La lectura geométrica de la página 110 fija para Puerto Natales: 00:28/0.26, 04:21/0.23, 12:18/0.56, 20:25/0.19 (UTC-4).
Aplicando Kirke -2:05 y Magallanes +1h, el 04-10 local queda 03:16 LW 0.28, 11:13 HW 0.56, 19:20 LW 0.24.
