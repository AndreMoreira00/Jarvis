# Entry point fino: so chama app_core_start(). Toda a logica vive nos componentes.
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       REQUIRES app_core)
