// Contact form (contact-us/): checks the required fields next to them and sends the message by
// e-mail through FormSubmit to bulfire@ecoes.eu, as the contact form on ecoes.eu. The fields are the
// old site's (name, e-mail, country and city, message, consent). A page that links here with
// ?topic= (the vehicle pages' "Get a quote") sets the e-mail's subject, so the request arrives
// marked; the visitor sees no extra field. If sending fails, the message says why (e.g. the form
// still waits for FormSubmit's one-time activation) and links to bulfire@ecoes.eu with everything
// filled in, and the form keeps what was typed. Texts follow data-lang on the form (en/bg).
// Without JavaScript the form posts to FormSubmit normally.
(function () {
  var form = document.querySelector('.contact-form');
  if (!form) return;

  var TO = 'bulfire@ecoes.eu';
  var TEXT = {
    en: {
      subject: 'BULFIRE website: ',
      general: 'message',
      topics: {
        vehicles: 'All-terrain and off-road fire fighting vehicles',
        services: 'Services and transformations of fire trucks',
        tractors: 'Off-road fire fighting tractors',
        shop: 'BULFIRE online fire shops'
      },
      sent: 'Thank you! Your message has been sent. We will contact you soon.',
      sending: 'Sending…',
      send: 'Send',
      notActive: 'The message was not sent because the contact form has not been activated yet. Please send it by e-mail to ',
      failed: 'The message could not be sent. Please try again later, or send it by e-mail to ',
      filledIn: ' (the link opens your e-mail program with your message filled in).',
      detail: 'Details: '
    },
    bg: {
      subject: 'Сайт BULFIRE: ',
      general: 'съобщение',
      topics: {
        vehicles: 'Всъдеходни и високопроходими противопожарни автомобили',
        services: 'Сервиз и трансформации на пожарни автомобили',
        tractors: 'Високопроходими противопожарни трактори',
        shop: 'Онлайн магазини BULFIRE'
      },
      sent: 'Благодарим ви! Съобщението е изпратено. Ще се свържем с вас скоро.',
      sending: 'Изпращане…',
      send: 'Изпрати',
      notActive: 'Съобщението не беше изпратено, защото формата за контакт все още не е активирана. Моля, изпратете го по имейл до ',
      failed: 'Съобщението не можа да бъде изпратено. Моля, опитайте отново по-късно или го изпратете по имейл до ',
      filledIn: ' (връзката отваря вашата имейл програма с попълнено съобщение).',
      detail: 'Подробности: '
    }
  };
  var T = TEXT[form.getAttribute('data-lang')] || TEXT.en;

  var status = form.querySelector('.form-status');
  var button = form.querySelector('button[type="submit"]');
  var buttonLabel = button.querySelector('.btn-label');
  var subject = form.querySelector('input[name="_subject"]');
  var topic = T.topics[new URLSearchParams(window.location.search).get('topic')];
  subject.value = T.subject + (topic || T.general);

  var fields = [
    { el: form.querySelector('#c-name'), error: form.querySelector('#ce-name'), ok: function (el) { return el.value.trim() !== ''; } },
    { el: form.querySelector('#c-email'), error: form.querySelector('#ce-email'), ok: function (el) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim()); } },
    { el: form.querySelector('#c-message'), error: form.querySelector('#ce-message'), ok: function (el) { return el.value.trim() !== ''; } },
    { el: form.querySelector('#c-consent'), error: form.querySelector('#ce-consent'), ok: function (el) { return el.checked; } }
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

  function show(text, isError) {
    status.textContent = text;
    status.classList.toggle('is-error', isError);
    status.hidden = false;
  }

  // a mailto link to bulfire@ecoes.eu with the visitor's entries filled in
  function mailto() {
    var lines = [];
    ['#c-name', '#c-email', '#c-place'].forEach(function (id) {
      var el = form.querySelector(id);
      var label = form.querySelector('label[for="' + el.id + '"]');
      if (el.value.trim()) lines.push((label ? label.textContent.replace('*', '').trim() : el.name) + ': ' + el.value.trim());
    });
    return 'mailto:' + TO + '?subject=' + encodeURIComponent(subject.value) +
      '&body=' + encodeURIComponent(lines.join('\r\n') + '\r\n\r\n' + form.querySelector('#c-message').value.trim());
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
    if (form.querySelector('#c-hp').value) return;   // filled in by a bot

    button.disabled = true;
    buttonLabel.textContent = T.sending;
    status.hidden = true;

    var data = {};
    new FormData(form).forEach(function (value, key) { data[key] = value; });

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
        subject.value = T.subject + (topic || T.general);
        fields.forEach(function (field) { field.el.removeAttribute('aria-invalid'); });
        show(T.sent, false);
      })
      .catch(function (err) {
        if (window.console) console.warn('Contact form:', err);
        showError(err && err.name === 'AbortError' ? 'timeout' : String(err && err.message || err));
      })
      .then(function () {
        if (timer) clearTimeout(timer);
        button.disabled = false;
        buttonLabel.textContent = T.send;
      });
  });
})();
