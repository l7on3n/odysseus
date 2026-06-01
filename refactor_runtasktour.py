import re

with open('static/js/slashCommands.js', 'r') as f:
    content = f.read()

replacement = """async function _runTaskTour(tour, steps, doneText, opts) {
  opts = opts || {};
  const _msgEl = document.getElementById('message');
  if (_msgEl) {
    _msgEl.value = '';
    _msgEl.dispatchEvent(new Event('input', { bubbles: true }));
  }

  const modal = await _openTasksForTour();
  if (!modal) {
    slashReply('Could not open Tasks. Try clicking the Tasks tool first.');
    return true;
  }

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    const res = await tour.showStep(step.sel, step.text, {
      isFirst: i === 0,
      isLast: i === steps.length - 1,
      before: step.before
    });
    
    if (step.after) { try { step.after(); } catch (_) {} }
    
    if (res === 'skip') { tour.clear(); return 'skipped'; }
    if (res === 'back' && i > 0) i -= 2;
  }

  if (opts.continueLabel) {
    const res = await tour.showStep(null, opts.continueText || 'Want to keep going?', {
      isFirst: false,
      isLast: false,
      placement: 'center-above',
      finishLabel: true, // we customize this via replacing tooltip innerHTML? 
      // Wait, let's just use the tour interface properly.
    });
    // Let's manually override the tooltip for the continue prompt since it's custom.
    tour.clearHalos();
    tour.tooltip.classList.remove('tour-fade-in');
    tour.tooltip.innerHTML =
      '<div class="tour-text">' + (opts.continueText || 'Want to keep going?') + '</div>' +
      '<div class="tour-nav">' +
        '<button class="tour-btn-skip" data-act="stop">no thanks</button>' +
        '<button class="tour-btn-arrow" data-act="continue">' + opts.continueLabel + '</button>' +
      '</div>';
    tour.tooltip.style.visibility = 'hidden';
    requestAnimationFrame(() => {
      const tw = tour.tooltip.offsetWidth || 260;
      const th = tour.tooltip.offsetHeight || 100;
      tour.tooltip.style.top = Math.max(10, window.innerHeight * 0.32 - th / 2) + 'px';
      tour.tooltip.style.left = Math.max(10, window.innerWidth / 2 - tw / 2) + 'px';
      tour.tooltip.style.visibility = '';
      tour.tooltip.classList.add('tour-fade-in');
    });
    const choice = await new Promise(resolve => {
      const onClick = (e) => {
        const hit = e.target.closest && e.target.closest('[data-act]');
        if (!hit) return;
        tour.tooltip.removeEventListener('click', onClick);
        resolve(hit.dataset.act);
      };
      tour.tooltip.addEventListener('click', onClick);
    });
    tour.clear();
    if (choice === 'continue') return 'continue';
  } else {
    tour.clear();
  }
  
  if (doneText) await typewriterReply(doneText);
  return 'done';
}"""

# Replace the _runTaskTour function entirely
start_str = "async function _runTaskTour(steps, doneText, opts) {"
end_str = "  return 'done';\n}"
if start_str in content and end_str in content:
    start_idx = content.find(start_str)
    end_idx = content.find(end_str, start_idx) + len(end_str)
    content = content[:start_idx] + replacement + content[end_idx:]

# Update the callers
content = content.replace("const result = await _runTaskTour([", "const result = await _runTaskTour(tour, [")
content = content.replace("return _runTaskTour([", "return _runTaskTour(tour, [")

with open('static/js/slashCommands.js', 'w') as f:
    f.write(content)
