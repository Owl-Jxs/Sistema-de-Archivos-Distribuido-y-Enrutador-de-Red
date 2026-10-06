from datetime import datetime, timedelta, timezone


ZONA_HORARIA_COSTA_RICA = timezone(timedelta(hours=-6), "Costa Rica")


def fecha_hora_actual_costa_rica() -> datetime:
    return datetime.now(ZONA_HORARIA_COSTA_RICA)
