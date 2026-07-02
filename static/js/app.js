'use strict';

document.addEventListener('DOMContentLoaded', () => {
  /* ─── Contador del carrito ──────────────────────────── */
  const actualizarContadorCarrito = async () => {
    const badge = document.getElementById('carrito-count');
    if (!badge) return;
    try {
      const res = await fetch('/carrito/');
      const html = await res.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const filas = doc.querySelectorAll('table tbody tr');
      let total = 0;
       filas.forEach(row => {
        const input = row.querySelector('.form-cantidad input[name="cantidad"]');
        if (input) total += parseInt(input.value, 10) || 0;
      });
      badge.textContent = total;
      badge.style.display = total > 0 ? 'inline-flex' : 'none';
    } catch {
      const stored = sessionStorage.getItem('carrito_count');
      badge.textContent = stored || '0';
    }
  };
  actualizarContadorCarrito();

  /* ─── Cerrar alertas ────────────────────────────────── */
  document.querySelectorAll('.cerrar-alerta').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.alerta').remove();
    });
  });

  /* ─── Auto-ocultar alertas ──────────────────────────── */
  document.querySelectorAll('.alerta').forEach(alerta => {
    setTimeout(() => {
      alerta.style.transition = 'opacity 0.3s';
      alerta.style.opacity = '0';
      setTimeout(() => alerta.remove(), 300);
    }, 5000);
  });

  /* ─── Confirmación de eliminación ───────────────────── */
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm || '¿Estás seguro?')) {
        e.preventDefault();
      }
    });
  });

  /* ─── Auto-enfoque ──────────────────────────────────── */
  const firstInput = document.querySelector('.form-estandar .form-control, .form-auth .form-control');
  if (firstInput) firstInput.focus();
});
