(function () {
  var MSG = __MSG__;
  var header = document.querySelector('.site-header');
  var burger = document.querySelector('.burger');
  var nav = document.getElementById('nav');

  function onScroll() { header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  function setMenu(open) {
    burger.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
  }
  burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); burger.focus(); }
  });
  window.matchMedia('(min-width: 1041px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });

  document.querySelectorAll('a[aria-disabled="true"]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); });
  });

  /* ---- quote form ---- */
  var form = document.getElementById('quote-form');
  var ok = document.getElementById('quote-success');

  function setErr(id, fieldEl, msg) {
    var p = document.getElementById(id);
    if (p) p.textContent = msg || '';
    if (fieldEl) {
      fieldEl.classList.toggle('invalid', !!msg);
      var ctl = fieldEl.querySelector('input:not([type=radio]):not([type=checkbox]),select,textarea,input[type=checkbox][required]');
      if (ctl) ctl.setAttribute('aria-invalid', msg ? 'true' : 'false');
    }
  }

  function checkInput(el) {
    var f = el.closest('.field');
    var v = el.value.trim();
    var msg = '';
    if (el.type === 'checkbox') { msg = el.checked ? '' : MSG.rgpd; }
    else if (el.required && !v) { msg = el.tagName === 'SELECT' ? MSG.select : MSG.required; }
    else if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) { msg = MSG.email; }
    else if (el.name === 'cif' && !/^[A-Z0-9][0-9]{7}[A-Z0-9]$/i.test(v)) { msg = MSG.cif; }
    else if (el.type === 'tel' && (v.replace(/\D/g, '').length < 9)) { msg = MSG.tel; }
    setErr('e-' + el.id, f, msg);
    return !msg;
  }

  function checkGroups() {
    var okAll = true;
    var tipo = form.querySelector('input[name=tipo]:checked');
    setErr('e-tipo', document.getElementById('g-tipo'), tipo ? '' : MSG.tipo);
    if (!tipo) okAll = false;
    var prod = form.querySelector('input[name=productos]:checked');
    setErr('e-prod', document.getElementById('g-prod'), prod ? '' : MSG.prod);
    if (!prod) okAll = false;
    return okAll;
  }

  var fields = form.querySelectorAll('#empresa,#cif,#persona,#email,#telefono,#provincia,#volumen,#rgpd');
  fields.forEach(function (el) {
    el.addEventListener('blur', function () { if (el.value || el.closest('.field').classList.contains('invalid')) checkInput(el); });
    el.addEventListener('change', function () { if (el.closest('.field').classList.contains('invalid')) checkInput(el); });
  });
  form.addEventListener('change', function (e) {
    if (e.target.name === 'tipo' || e.target.name === 'productos') {
      var g = e.target.closest('fieldset');
      if (g.classList.contains('invalid')) checkGroups();
    }
  });
  document.getElementById('cif').addEventListener('input', function (e) { e.target.value = e.target.value.toUpperCase().replace(/\s/g, ''); });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var valid = checkGroups();
    var first = null;
    fields.forEach(function (el) { if (!checkInput(el)) { valid = false; first = first || el; } });
    if (!valid) {
      var target = form.querySelector('.invalid input, .invalid select, .invalid textarea') || first;
      if (target) target.focus();
      return;
    }
    form.hidden = true;
    ok.hidden = false;
    ok.focus();
  });

  document.getElementById('quote-again').addEventListener('click', function () {
    form.reset();
    form.querySelectorAll('.invalid').forEach(function (f) { f.classList.remove('invalid'); });
    form.querySelectorAll('.err').forEach(function (p) { p.textContent = ''; });
    ok.hidden = true;
    form.hidden = false;
    document.getElementById('empresa').focus();
  });
})();
