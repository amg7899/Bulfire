// The online fire shops: search, the quote request and its form.
// No prices anywhere (client, 2026-11-26). Every product has a "Get a quote" button (hidden in the
// markup, shown here) that adds it to the visitor's quote request or takes it out again. While the
// request has products and the form is out of view, a bar at the bottom of the window counts them and
// leads to the form, where the quantities are set. The request goes by e-mail through FormSubmit to
// bulfire@ecoes.eu, as the contact form on ecoes.eu: errors next to the fields; if sending fails, the
// message says why and links to bulfire@ecoes.eu with everything filled in, and nothing typed is lost.
// The list is kept for the visitor in localStorage, so it survives a reload and the switch to the
// other language (both pages use the same product ids). Texts follow data-lang on the form (en/bg).
// Without JavaScript the cards show without the buttons, and the form posts with the message field.
(function () {
  var form = document.querySelector('.quote-form');
  if (!form) return;

  var TO = 'bulfire@ecoes.eu';
  var KEY = 'bulfire-quote';
  var lang = form.getAttribute('data-lang') === 'bg' ? 'bg' : 'en';
  var TEXT = {
    en: {
      count: function (n) { return n === 1 ? '1 product' : n + ' products'; },
      added: function (name, n) { return 'Added to the quote request: ' + name + '. ' + TEXT.en.count(n) + ' in the request.'; },
      removed: function (name, n) { return 'Removed from the quote request: ' + name + '. ' + TEXT.en.count(n) + ' in the request.'; },
      quantity: 'Quantity',
      remove: 'Remove',
      none: function (q) { return 'No products found for “' + q + '”. Try another word, or write what you need in the quote request below.'; },
      sent: 'Thank you! Your quote request has been sent. We will contact you soon.',
      sending: 'Sending…',
      send: 'Send quote request',
      notActive: 'The request was not sent because the form has not been activated yet. Please send it by e-mail to ',
      failed: 'The request could not be sent. Please try again later, or send it by e-mail to ',
      filledIn: ' (the link opens your e-mail program with your request filled in).',
      detail: 'Details: ',
      fields: { name: 'Name', company: 'Company', email: 'E-mail', phone: 'Phone', country: 'Country', products: 'Products', message: 'Message' }
    },
    bg: {
      count: function (n) { return n === 1 ? '1 продукт' : n + ' продукта'; },
      added: function (name, n) { return 'Добавено в запитването за оферта: ' + name + '. В запитването: ' + TEXT.bg.count(n) + '.'; },
      removed: function (name, n) { return 'Премахнато от запитването за оферта: ' + name + '. В запитването: ' + TEXT.bg.count(n) + '.'; },
      quantity: 'Количество',
      remove: 'Премахни',
      none: function (q) { return 'Няма намерени продукти за „' + q + '“. Опитайте с друга дума или опишете в запитването по-долу какво ви е необходимо.'; },
      sent: 'Благодарим ви! Запитването за оферта е изпратено. Ще се свържем с вас скоро.',
      sending: 'Изпращане…',
      send: 'Изпратете запитването',
      notActive: 'Запитването не беше изпратено, защото формата все още не е активирана. Моля, изпратете го по имейл до ',
      failed: 'Запитването не можа да бъде изпратено. Моля, опитайте отново по-късно или го изпратете по имейл до ',
      filledIn: ' (връзката отваря вашата имейл програма с попълнено запитване).',
      detail: 'Подробности: ',
      fields: { name: 'Име', company: 'Фирма', email: 'Имейл', phone: 'Телефон', country: 'Държава', products: 'Продукти', message: 'Съобщение' }
    }
  };
  var T = TEXT[lang];

  var REMOVE_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M6 6l12 12M18 6 6 18"/></svg>';

  // ---------- products on the page ----------
  var cards = {};
  Array.prototype.forEach.call(document.querySelectorAll('.product'), function (li) {
    var id = li.getAttribute('data-id');
    var button = li.querySelector('.quote-btn');
    cards[id] = {
      li: li,
      button: button,
      name: li.querySelector('.product-name').textContent.trim(),
      en: li.getAttribute('data-en') || '',
      search: normalise(li.getAttribute('data-search') || '')
    };
    button.hidden = false;
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', function () { toggle(id); });
  });

  function normalise(text) {
    text = text.toLowerCase();
    return text.normalize ? text.normalize('NFD').replace(/[̀-ͯ]/g, '') : text;
  }

  // ---------- the quote request: [{id, qty}], in the order the products were added ----------
  var items = load();
  function load() {
    try {
      var raw = JSON.parse(window.localStorage.getItem(KEY) || '[]');
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (x) { return x && cards[x.id]; }).map(function (x) {
        return { id: String(x.id), qty: clampQty(x.qty) };
      });
    } catch (e) { return []; }
  }
  function save() {
    try { window.localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) { /* storage blocked */ }
  }
  function clampQty(v) { return Math.max(1, Math.min(9999, parseInt(v, 10) || 1)); }
  function indexOf(id) {
    for (var i = 0; i < items.length; i++) if (items[i].id === id) return i;
    return -1;
  }

  var live = document.querySelector('.quote-live');
  function announce(text) {
    if (!live) return;
    live.textContent = '';
    window.setTimeout(function () { live.textContent = text; }, 60);
  }

  function toggle(id) {
    var i = indexOf(id);
    if (i < 0) {
      items.push({ id: id, qty: 1 });
      announce(T.added(cards[id].name, items.length));
    } else {
      items.splice(i, 1);
      announce(T.removed(cards[id].name, items.length));
    }
    save();
    render();
    // a product now counts as what the visitor needs: clear the message error if it was shown
    if (message.getAttribute('aria-invalid') === 'true') check(fields[2]);
  }

  // ---------- the list in the form ----------
  var fieldset = form.querySelector('.quote-items');
  var list = form.querySelector('.quote-list');
  var empty = form.querySelector('.quote-empty');
  fieldset.hidden = false;

  function renderList() {
    list.textContent = '';
    items.forEach(function (item) {
      var card = cards[item.id];
      var li = document.createElement('li');
      li.className = 'quote-item';
      li.setAttribute('data-id', item.id);
      var name = document.createElement('span');
      name.className = 'quote-item-name';
      name.textContent = card.name;
      var label = document.createElement('label');
      label.className = 'quote-qty';
      var labelText = document.createElement('span');
      labelText.textContent = T.quantity;
      var qty = document.createElement('input');
      qty.type = 'number';
      qty.min = '1';
      qty.max = '9999';
      qty.step = '1';
      qty.inputMode = 'numeric';
      qty.value = String(item.qty);
      qty.addEventListener('change', function () {
        item.qty = clampQty(qty.value);
        qty.value = String(item.qty);
        save();
      });
      label.appendChild(labelText);
      label.appendChild(qty);
      var remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'quote-remove';
      remove.setAttribute('aria-label', T.remove + ': ' + card.name);
      remove.innerHTML = REMOVE_ICON;
      remove.addEventListener('click', function () {
        var at = indexOf(item.id);
        toggle(item.id);
        // keep the keyboard in the list: the next product's button, else the previous one, else the legend's field
        var buttons = list.querySelectorAll('.quote-remove');
        var target = buttons[Math.min(at, buttons.length - 1)];
        (target || form.querySelector('#q-message')).focus();
      });
      li.appendChild(name);
      li.appendChild(label);
      li.appendChild(remove);
      list.appendChild(li);
    });
    empty.hidden = items.length > 0;
  }

  // ---------- the bar at the bottom of the window ----------
  var bar = document.querySelector('.quote-bar');
  var barCount = bar && bar.querySelector('.quote-bar-count');
  var formInView = false;
  function renderBar() {
    if (!bar) return;
    barCount.textContent = T.count(items.length);
    bar.hidden = !items.length || formInView;
  }
  if (bar && window.IntersectionObserver) {
    new IntersectionObserver(function (entries) {
      formInView = entries[0].isIntersecting;
      renderBar();
    }, { rootMargin: '0px 0px -80px 0px' }).observe(document.getElementById('quote'));
  }

  function render() {
    Object.keys(cards).forEach(function (id) {
      cards[id].button.setAttribute('aria-pressed', String(indexOf(id) >= 0));
    });
    renderList();
    renderBar();
  }
  render();

  // ---------- search ----------
  var searchBox = document.querySelector('.shop-search');
  var search = document.getElementById('shop-q');
  var none = document.querySelector('.shop-empty');
  if (searchBox && search) {
    searchBox.hidden = false;
    var sections = Array.prototype.slice.call(document.querySelectorAll('.shop-section'));
    var filter = function () {
      var q = search.value.trim();
      var words = normalise(q).split(/\s+/).filter(Boolean);
      var total = 0;
      sections.forEach(function (section) {
        var shown = 0;
        Array.prototype.forEach.call(section.querySelectorAll('.product'), function (li) {
          var card = cards[li.getAttribute('data-id')];
          var match = words.every(function (w) { return card.search.indexOf(w) >= 0; });
          li.hidden = !match;
          if (match) shown++;
        });
        section.hidden = shown === 0;
        var count = document.querySelector('.shop-count[data-count="' + section.id + '"]');
        if (count) count.textContent = String(shown);
        total += shown;
      });
      none.hidden = total > 0;
      if (!total) none.textContent = T.none(q);
    };
    search.addEventListener('input', filter);
    if (search.value) filter();   // the browser may restore a typed query
  }

  // ---------- the form ----------
  var status = form.querySelector('.form-status');
  var button = form.querySelector('button[type="submit"]');
  var buttonLabel = button.querySelector('.btn-label');
  var productsField = form.querySelector('input[name="products"]');
  var message = form.querySelector('#q-message');

  var fields = [
    { el: form.querySelector('#q-name'), error: form.querySelector('#e-name'), ok: function (el) { return el.value.trim() !== ''; } },
    { el: form.querySelector('#q-email'), error: form.querySelector('#e-email'), ok: function (el) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim()); } },
    { el: message, error: form.querySelector('#e-message'), ok: function (el) { return items.length > 0 || el.value.trim() !== ''; } },
    { el: form.querySelector('#q-consent'), error: form.querySelector('#e-consent'), ok: function (el) { return el.checked; } }
  ];

  function check(field) {
    var valid = field.ok(field.el);
    field.el.setAttribute('aria-invalid', String(!valid));
    field.error.hidden = valid;
    return valid;
  }
  // once a field has been flagged, re-check it as the visitor fixes it
  fields.forEach(function (field) {
    field.el.addEventListener(field.el.type === 'checkbox' ? 'change' : 'input', function () {
      if (field.el.getAttribute('aria-invalid') === 'true') check(field);
    });
  });

  // "2 × Storz cap 52 mm"; on the Bulgarian page with the English name in brackets, as in the old shop
  function productLines() {
    return items.map(function (item) {
      var card = cards[item.id];
      var name = lang === 'bg' && card.en && card.en !== card.name ? card.name + ' (' + card.en + ')' : card.name;
      return item.qty + ' × ' + name;
    }).join('\n');
  }

  function show(text, isError) {
    status.textContent = text;
    status.classList.toggle('is-error', isError);
    status.hidden = false;
  }

  // a mailto link to bulfire@ecoes.eu with the visitor's entries filled in
  function mailto() {
    var lines = [];
    ['name', 'company', 'email', 'phone', 'country'].forEach(function (key) {
      var el = form.querySelector('[name="' + key + '"]');
      if (el && el.value.trim()) lines.push(T.fields[key] + ': ' + el.value.trim());
    });
    var body = lines.join('\r\n');
    if (items.length) body += '\r\n\r\n' + T.fields.products + ':\r\n' + productLines().replace(/\n/g, '\r\n');
    if (message.value.trim()) body += '\r\n\r\n' + message.value.trim();
    return 'mailto:' + TO + '?subject=' + encodeURIComponent(form.querySelector('input[name="_subject"]').value) +
      '&body=' + encodeURIComponent(body);
  }

  function showError(reason) {
    var notActive = /activat/i.test(reason);
    show(notActive ? T.notActive : T.failed, true);
    var link = document.createElement('a');
    link.href = mailto();
    link.textContent = TO;
    link.setAttribute('translate', 'no');
    status.appendChild(link);
    status.appendChild(document.createTextNode(T.filledIn));
    if (!notActive && reason) {
      var detail = document.createElement('small');
      detail.className = 'form-detail';
      detail.textContent = T.detail + reason;
      status.appendChild(detail);
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var firstInvalid = null;
    fields.forEach(function (field) {
      if (!check(field) && !firstInvalid) firstInvalid = field.el;
    });
    if (firstInvalid) {
      firstInvalid.focus();
      return;
    }
    if (form.querySelector('#q-hp').value) return;   // filled in by a bot

    productsField.value = productLines();
    button.disabled = true;
    buttonLabel.textContent = T.sending;
    status.hidden = true;

    var data = {};
    new FormData(form).forEach(function (value, key) { data[key] = value; });
    if (!data.products) delete data.products;

    var controller = window.AbortController ? new AbortController() : null;
    var timer = controller && setTimeout(function () { controller.abort(); }, 25000);

    fetch(form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data),
      signal: controller ? controller.signal : undefined
    })
      .then(function (response) {
        return response.json().catch(function () { return { success: false, message: 'HTTP ' + response.status }; });
      })
      .then(function (result) {
        // FormSubmit answers {success: "true"} or {success: "false", message: "..."}
        if (String(result.success) !== 'true') throw new Error(result.message || 'not sent');
        form.reset();
        fields.forEach(function (field) { field.el.removeAttribute('aria-invalid'); });
        items = [];
        save();
        render();
        show(T.sent, false);
      })
      .catch(function (err) {
        if (window.console) console.warn('Quote form:', err);
        showError(err && err.name === 'AbortError' ? 'timeout' : String(err && err.message || err));
      })
      .then(function () {
        if (timer) clearTimeout(timer);
        button.disabled = false;
        buttonLabel.textContent = T.send;
      });
  });
})();
