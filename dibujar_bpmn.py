#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dibujar_bpmn.py
Genera una imagen gráfica profesional (PNG en alta resolución) del Diagrama de
Procesos de Negocio (BPMN) para FerreMax usando matplotlib.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(BASE_DIR, "diagrams", "diagrama-procesos-bpmn.png")

def generar_diagrama_bpmn():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Colores BPMN profesionales
    c_start = "#22C55E"      # Verde inicio
    c_task = "#E0F2FE"       # Azul claro tarea
    c_task_border = "#0284C7"
    c_gateway = "#FEF3C7"    # Amarillo compuerta
    c_gateway_border = "#D97706"
    c_cancel = "#FEE2E2"     # Rojo cancelación
    c_cancel_border = "#DC2626"
    c_end = "#15803D"        # Verde fin
    c_arrow = "#374151"

    # Título del Diagrama
    ax.text(6.5, 7.1, "Diagrama de Procesos de Negocio (BPMN) — Flujo Comercial FerreMax",
            fontsize=13, fontweight="bold", ha="center", va="center", color="#111827", family="sans-serif")
    ax.text(6.5, 6.75, "Ciclo de Vida de la Operación: Cotización, Validación, Surtido y Despacho",
            fontsize=9.5, fontstyle="italic", ha="center", va="center", color="#4B5563", family="sans-serif")

    # Función auxiliar para dibujar cajas de tareas BPMN
    def dibujar_tarea(x, y, w, h, texto, color_bg=c_task, color_border=c_task_border):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=color_bg, edgecolor=color_border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, texto, ha="center", va="center", fontsize=8.5,
                fontweight="bold", color="#1F2937", zorder=3, family="sans-serif", multialignment="center")

    # Función auxiliar para compuertas (rombos)
    def dibujar_compuerta(cx, cy, size=0.45, label=""):
        romb = patches.Polygon([
            (cx, cy + size),
            (cx + size*1.2, cy),
            (cx, cy - size),
            (cx - size*1.2, cy)
        ], closed=True, facecolor=c_gateway, edgecolor=c_gateway_border, linewidth=1.8, zorder=2)
        ax.add_patch(romb)
        ax.text(cx, cy, "✕", ha="center", va="center", fontsize=11, fontweight="bold", color="#B45309", zorder=3)
        if label:
            ax.text(cx, cy + size + 0.22, label, ha="center", va="bottom", fontsize=8,
                    fontweight="bold", color="#B45309", family="sans-serif")

    # Flechas conectores
    def flecha(x1, y1, x2, y2, texto=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=14),
                    zorder=1)
        if texto:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.12, texto, ha="center", va="bottom", fontsize=7.5,
                    fontweight="bold", color="#1F2937", family="sans-serif",
                    bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85))

    # 1. Evento de Inicio (Círculo verde)
    start_circle = patches.Circle((0.9, 5.0), radius=0.3, facecolor="#DCFCE7", edgecolor=c_start, linewidth=2.5, zorder=2)
    ax.add_patch(start_circle)
    ax.text(0.9, 5.0, "▶", ha="center", va="center", fontsize=10, color=c_start, zorder=3)
    ax.text(0.9, 4.4, "Inicio:\nSolicitud de Compra\no Cotización", ha="center", va="top", fontsize=7.5, fontweight="bold", color="#1F2937")

    # Flecha 1
    flecha(1.2, 5.0, 1.8, 5.0)

    # 2. Tarea: Registrar Operación (CREADO)
    dibujar_tarea(1.8, 4.5, 2.0, 1.0, "Registrar Operación\n(Estado: CREADO)")
    flecha(3.8, 5.0, 4.5, 5.0)

    # 3. Compuerta 1: ¿Válida? (Cotización vigente y crédito OK)
    dibujar_compuerta(4.9, 5.0, size=0.42, label="¿Vigente y Crédito OK?")

    # Rama Sí (hacia la derecha)
    flecha(5.4, 5.0, 6.2, 5.0, "Sí (Aprobado)")

    # Rama No (hacia abajo a Cancelar)
    ax.annotate("", xy=(4.9, 2.6), xytext=(4.9, 4.58),
                arrowprops=dict(arrowstyle="-|>", color=c_cancel_border, lw=1.6, mutation_scale=14),
                zorder=1)
    ax.text(5.05, 3.6, "No (Vencida /\nSin Crédito)", ha="left", va="center", fontsize=7.5,
            fontweight="bold", color=c_cancel_border,
            bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85))

    # Tarea: Cancelar Operación
    dibujar_tarea(3.9, 1.6, 2.0, 1.0, "Rechazar y Cancelar\n(Estado: CANCELADO)", color_bg=c_cancel, color_border=c_cancel_border)

    # Fin de Cancelación
    flecha(5.9, 2.1, 6.7, 2.1)
    cancel_circle = patches.Circle((7.0, 2.1), radius=0.3, facecolor="#FEE2E2", edgecolor=c_cancel_border, linewidth=3.0, zorder=2)
    ax.add_patch(cancel_circle)
    ax.text(7.0, 2.1, "■", ha="center", va="center", fontsize=9, color=c_cancel_border, zorder=3)
    ax.text(7.0, 1.5, "Fin:\nOperación Cancelada", ha="center", va="top", fontsize=7.5, fontweight="bold", color=c_cancel_border)

    # 4. Tarea: Aprobar Operación (APROBADO)
    dibujar_tarea(6.2, 4.5, 2.0, 1.0, "Aprobar Operación\n(Estado: APROBADO)")
    flecha(8.2, 5.0, 8.9, 5.0)

    # 5. Compuerta 2: ¿Stock en Bodega?
    dibujar_compuerta(9.3, 5.0, size=0.42, label="¿Stock Suficiente?")

    # Rama Sí: Surtido Completo
    flecha(9.8, 5.0, 10.6, 5.0, "Suficiente")

    # Rama Parcial: hacia abajo
    ax.annotate("", xy=(9.3, 3.7), xytext=(9.3, 4.58),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=14),
                zorder=1)
    ax.text(9.45, 4.15, "Insuficiente", ha="left", va="center", fontsize=7.5,
            fontweight="bold", color="#B45309",
            bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85))

    # Tarea Parcial
    dibujar_tarea(8.3, 2.7, 2.0, 1.0, "Marcar PARCIAL y\nPedir Resurtido", color_bg="#FEF9C3", color_border="#CA8A04")
    # De parcial va hacia surtido
    ax.annotate("", xy=(11.3, 4.5), xytext=(10.3, 3.2),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.4, mutation_scale=12),
                zorder=1)

    # 6. Tarea: Surtir en Almacén (SURTIDO)
    dibujar_tarea(10.6, 4.5, 1.9, 1.0, "Surtir en Bodega\n(Estado: SURTIDO)")

    # Conector a la fila inferior para Entrega
    ax.annotate("", xy=(11.5, 1.0), xytext=(11.5, 4.5),
                arrowprops=dict(arrowstyle="-", color=c_arrow, lw=1.6),
                zorder=1)
    ax.annotate("", xy=(10.5, 1.0), xytext=(11.5, 1.0),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=14),
                zorder=1)

    # 7. Tarea: Despachar y Entregar (ENTREGADO)
    dibujar_tarea(8.3, 0.5, 2.2, 1.0, "Despachar y Entregar\n(Estado: ENTREGADO)", color_bg="#DCFCE7", color_border="#16A34A")

    # 8. Evento de Fin Éxito
    flecha(8.3, 1.0, 7.5, 1.0)
    end_circle_outer = patches.Circle((7.1, 1.0), radius=0.32, facecolor="#DCFCE7", edgecolor=c_end, linewidth=3.5, zorder=2)
    ax.add_patch(end_circle_outer)
    ax.text(7.1, 1.0, "✔", ha="center", va="center", fontsize=11, fontweight="bold", color=c_end, zorder=3)
    ax.text(7.1, 0.45, "Fin:\nTicket Emitido y\nMaterial Entregado", ha="center", va="top", fontsize=7.5, fontweight="bold", color=c_end)

    # Marco exterior decorativo
    border_rect = patches.Rectangle((0.15, 0.15), 12.7, 7.2, linewidth=1.2, edgecolor="#CBD5E1", facecolor="none", zorder=0)
    ax.add_patch(border_rect)

    plt.tight_layout()
    plt.savefig(OUT_PATH, format="png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Diagrama BPMN profesional generado en: {OUT_PATH}")

if __name__ == "__main__":
    generar_diagrama_bpmn()
