"""
Servicio de Dashboard — KPIs y estadísticas.
"""

from datetime import date, timedelta
from sqlalchemy import func, case
from app.extensions import db
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva
from app.models.facturacion import Factura
from app.models.mantenimiento import OrdenMantenimiento
from app.models.notificacion import Notificacion
from app.models.huesped import Huesped
from app.models.canal import Canal


class DashboardService:

    @staticmethod
    def get_kpis(fecha=None):
        """KPIs generales del hotel para una fecha dada."""
        if fecha is None:
            fecha = date.today()

        total_hab = Habitacion.query.filter_by(activa=True).count()
        disponibles = Habitacion.query.filter_by(estado='disponible').count()
        ocupadas = Habitacion.query.filter_by(estado='ocupada').count()
        en_mantenimiento = Habitacion.query.filter_by(estado='mantenimiento').count()
        en_limpieza = Habitacion.query.filter_by(estado='limpieza').count()

        ocupacion_pct = round((ocupadas / total_hab * 100), 1) if total_hab > 0 else 0

        llegadas_hoy = Reserva.query.filter(
            Reserva.fecha_entrada == fecha,
            Reserva.estado_id.in_([1, 2])
        ).count()

        salidas_hoy = Reserva.query.filter(
            Reserva.fecha_salida == fecha,
            Reserva.estado_id.in_([3, 4])
        ).count()

        en_casa = Reserva.query.filter_by(estado_id=3).count()

        ingresos_hoy = db.session.query(
            func.coalesce(func.sum(Factura.total), 0)
        ).filter(
            func.date(Factura.creado_en) == fecha,
            Factura.estado != 'anulada'
        ).scalar()

        ingresos_mes = db.session.query(
            func.coalesce(func.sum(Factura.total), 0)
        ).filter(
            func.month(Factura.creado_en) == fecha.month,
            func.year(Factura.creado_en) == fecha.year,
            Factura.estado != 'anulada'
        ).scalar()

        mant_abiertos = OrdenMantenimiento.query.filter_by(estado='abierta').count()
        notif_pendientes = Notificacion.query.filter_by(estado='pendiente').count()

        return {
            'fecha': fecha.isoformat(),
            'habitaciones': {
                'total': total_hab,
                'disponibles': disponibles,
                'ocupadas': ocupadas,
                'en_mantenimiento': en_mantenimiento,
                'en_limpieza': en_limpieza,
                'ocupacion_pct': ocupacion_pct,
            },
            'operaciones': {
                'llegadas_hoy': llegadas_hoy,
                'salidas_hoy': salidas_hoy,
                'en_casa': en_casa,
            },
            'financiero': {
                'ingresos_hoy': float(ingresos_hoy),
                'ingresos_mes': float(ingresos_mes),
            },
            'alertas': {
                'mantenimiento_abierto': mant_abiertos,
                'notificaciones_pendientes': notif_pendientes,
            }
        }

    @staticmethod
    def get_ingresos_por_mes(meses=12):
        """Ingresos desglosados por mes (últimos N meses)."""
        resultados = db.session.query(
            func.date_format(Factura.creado_en, '%Y-%m').label('mes'),
            func.count(Factura.id).label('facturas'),
            func.sum(case(
                (Factura.estado != 'anulada', Factura.subtotal), else_=0
            )).label('subtotal'),
            func.sum(case(
                (Factura.estado != 'anulada', Factura.total), else_=0
            )).label('total'),
        ).filter(
            Factura.creado_en >= func.date_sub(func.now(), text_type=f'{meses} MONTH')
        ).group_by('mes').order_by('mes').all()

        return [{
            'mes': r.mes,
            'facturas': r.facturas,
            'subtotal': float(r.subtotal or 0),
            'total': float(r.total or 0),
        } for r in resultados]

    @staticmethod
    def get_huespedes_frecuentes(limit=10):
        """Top huéspedes por número de estancias y gasto total."""
        resultados = db.session.query(
            Huesped.id,
            func.concat(Huesped.nombre, ' ', Huesped.apellido).label('huesped'),
            Huesped.email,
            Huesped.nivel_vip,
            func.count(Reserva.id).label('total_estancias'),
            func.coalesce(func.sum(Reserva.precio_total), 0).label('gasto_total'),
            func.max(Reserva.fecha_entrada).label('ultima_visita'),
        ).outerjoin(Reserva, (Reserva.huesped_id == Huesped.id) & (Reserva.estado_id.notin_([5, 6]))
        ).group_by(Huesped.id
        ).order_by(func.count(Reserva.id).desc()
        ).limit(limit).all()

        return [{
            'id': r.id,
            'huesped': r.huesped,
            'email': r.email,
            'nivel_vip': r.nivel_vip,
            'total_estancias': r.total_estancias,
            'gasto_total': float(r.gasto_total),
            'ultima_visita': r.ultima_visita.isoformat() if r.ultima_visita else None,
        } for r in resultados]

    @staticmethod
    def get_canales_rendimiento():
        """Rendimiento por canal de distribución."""
        resultados = db.session.query(
            Canal.nombre,
            Canal.comision,
            func.count(Reserva.id).label('reservas'),
            func.coalesce(func.sum(Reserva.precio_total), 0).label('ingresos_brutos'),
        ).outerjoin(Reserva, (Reserva.canal_id == Canal.id) & (Reserva.estado_id.notin_([5, 6]))
        ).group_by(Canal.id, Canal.nombre, Canal.comision
        ).order_by(func.count(Reserva.id).desc()).all()

        return [{
            'canal': r.nombre,
            'comision_pct': float(r.comision),
            'reservas': r.reservas,
            'ingresos_brutos': float(r.ingresos_brutos),
            'ingresos_netos': round(float(r.ingresos_brutos) * (1 - float(r.comision) / 100), 2),
        } for r in resultados]
