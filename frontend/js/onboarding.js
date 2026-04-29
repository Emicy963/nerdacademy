import { t } from './i18n.js';

const LS_KEY  = 'matrika_onboarding';
const LS_STEP = 'matrika_onboarding_step';

const STEPS = [
  {
    icon: '👋',
    titleKey: 'onboard.welcome.title',
    bodyKey:  'onboard.welcome.body',
    ctaKey:   'onboard.next',
    href:     null,
  },
  {
    icon: '📚',
    titleKey: 'onboard.course.title',
    bodyKey:  'onboard.course.body',
    ctaKey:   'onboard.course.cta',
    href:     '/pages/courses.html',
  },
  {
    icon: '🏫',
    titleKey: 'onboard.class.title',
    bodyKey:  'onboard.class.body',
    ctaKey:   'onboard.class.cta',
    href:     '/pages/classes.html',
  },
  {
    icon: '🎓',
    titleKey: 'onboard.student.title',
    bodyKey:  'onboard.student.body',
    ctaKey:   'onboard.student.cta',
    href:     '/pages/students.html',
  },
  {
    icon: '✅',
    titleKey: 'onboard.done.title',
    bodyKey:  'onboard.done.body',
    ctaKey:   'onboard.done.cta',
    href:     null,
  },
];

function getSavedStep() {
  return parseInt(localStorage.getItem(LS_STEP) ?? '0', 10);
}

function dismiss() {
  localStorage.removeItem(LS_KEY);
  localStorage.removeItem(LS_STEP);
  document.getElementById('onboarding-overlay')?.remove();
}

function renderStep(overlay, stepIndex) {
  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;
  const total  = STEPS.length;

  overlay.innerHTML = `
    <div class="onboard-card" role="dialog" aria-modal="true" aria-labelledby="onboard-title">
      <button class="onboard-skip" id="onboard-dismiss" aria-label="${t('onboard.skip') || 'Skip setup'}">
        ${t('onboard.skip') || 'Skip setup'}
      </button>

      <div class="onboard-progress">
        ${STEPS.map((_, i) => `<span class="onboard-dot${i <= stepIndex ? ' done' : ''}"></span>`).join('')}
      </div>

      <div class="onboard-icon" aria-hidden="true">${step.icon}</div>
      <h2 class="onboard-title" id="onboard-title">${t(step.titleKey) || step.titleKey}</h2>
      <p class="onboard-body">${t(step.bodyKey) || step.bodyKey}</p>

      <div class="onboard-actions">
        ${stepIndex > 0 ? `<button class="btn btn-ghost btn-sm" id="onboard-back">${t('onboard.back') || 'Back'}</button>` : ''}
        <button class="btn btn-primary" id="onboard-cta">
          ${t(step.ctaKey) || 'Next'}
        </button>
      </div>

      <p class="onboard-counter">${stepIndex + 1} / ${total}</p>
    </div>
  `;

  overlay.querySelector('#onboard-dismiss').addEventListener('click', dismiss);

  overlay.querySelector('#onboard-back')?.addEventListener('click', () => {
    const prev = stepIndex - 1;
    localStorage.setItem(LS_STEP, String(prev));
    renderStep(overlay, prev);
  });

  overlay.querySelector('#onboard-cta').addEventListener('click', () => {
    if (isLast) {
      dismiss();
      return;
    }
    if (step.href) {
      dismiss();
      window.location.href = step.href;
      return;
    }
    const next = stepIndex + 1;
    localStorage.setItem(LS_STEP, String(next));
    renderStep(overlay, next);
  });
}

export function initOnboarding() {
  if (localStorage.getItem(LS_KEY) !== 'pending') return;

  const overlay = document.createElement('div');
  overlay.id = 'onboarding-overlay';
  overlay.className = 'onboard-overlay';
  document.body.appendChild(overlay);

  renderStep(overlay, getSavedStep());
}
