/* ============================================================
   Agent 3 — Course Suggestion Dashboard
   app.js — Frontend logic
   ============================================================ */

const API_BASE = 'http://localhost:8000';

// ─── State ────────────────────────────────────────────────
let state = {
  allTech: [],
  allSoft: [],
  currentTab: 'tech',
  selectedTechSkills: [],
  selectedSoftSkills: [],
};

// ─── Platform icons (emoji map) ───────────────────────────
const PLATFORM_ICONS = {
  'freecodecamp': '🎓',
  'w3schools': '📚',
  'geeksforgeeks': '🧑‍💻',
  'kaggle': '📊',
  'microsoft learn': '🪟',
  'mdn web docs': '🌐',
  'swayam': '🎓',
  'nptel': '🏛️',
  'youtube': '▶️',
  'tcs ion': '🏢',
  'khan academy': '📖',
  'tutorialspoint': '📝',
  'programiz': '💡',
  'sqlzoo': '🗃️',
  'sqlbolt': '📋',
  'analytics vidhya': '📈',
  'coursera': '🎓',
  'edx': '🎓',
  'github': '🐙',
  'roadmap.sh': '🗺️',
  'real python': '🐍',
  'harvard cs50': '🏫',
};

function getPlatformIcon(platform) {
  const lower = (platform || '').toLowerCase();
  for (const [key, icon] of Object.entries(PLATFORM_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return '📌';
}

// ─── Toast notifications ──────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ─── Quick chip selector ──────────────────────────────────
document.querySelectorAll('.quick-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const skill = chip.dataset.skill;
    const type = chip.dataset.type;
    chip.classList.toggle('selected');

    if (type === 'tech') {
      const ta = document.getElementById('inp-tech');
      const skills = ta.value
        ? ta.value.split(',').map(s => s.trim()).filter(Boolean)
        : [];
      if (chip.classList.contains('selected')) {
        if (!skills.includes(skill)) skills.push(skill);
      } else {
        const idx = skills.indexOf(skill);
        if (idx > -1) skills.splice(idx, 1);
      }
      ta.value = skills.join(', ');
    } else {
      const ta = document.getElementById('inp-soft');
      const skills = ta.value
        ? ta.value.split(',').map(s => s.trim()).filter(Boolean)
        : [];
      if (chip.classList.contains('selected')) {
        if (!skills.includes(skill)) skills.push(skill);
      } else {
        const idx = skills.indexOf(skill);
        if (idx > -1) skills.splice(idx, 1);
      }
      ta.value = skills.join(', ');
    }
  });
});

// ─── Parse form inputs ────────────────────────────────────
function parseInputs() {
  const techRaw = document.getElementById('inp-tech').value;
  const softRaw = document.getElementById('inp-soft').value;
  const jobRole = document.getElementById('inp-job').value.trim();
  const pythonLevel = document.getElementById('inp-python-level').value;
  const sqlLevel = document.getElementById('inp-sql-level').value;

  const technical_skills = techRaw
    ? techRaw.split(',').map(s => s.trim()).filter(Boolean)
    : [];
  const soft_skills = softRaw
    ? softRaw.split(',').map(s => s.trim()).filter(Boolean)
    : [];

  const skill_levels = {};
  if (pythonLevel && technical_skills.some(s => s.toLowerCase() === 'python')) {
    skill_levels['Python'] = pythonLevel;
  }
  if (sqlLevel && technical_skills.some(s => s.toLowerCase() === 'sql')) {
    skill_levels['SQL'] = sqlLevel;
  }

  return {
    technical_skills,
    soft_skills,
    skill_levels,
    target_job_role: jobRole || undefined,
  };
}

// ─── Main: Get Recommendations ────────────────────────────
async function getRecommendations() {
  const payload = parseInputs();

  if (!payload.technical_skills.length && !payload.soft_skills.length) {
    showToast('Please enter at least one skill.', 'error');
    return;
  }

  showLoading(true);
  document.getElementById('results-section').style.display = 'none';

  try {
    const res = await fetch(`${API_BASE}/api/v1/courses/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${res.status})`);
    }

    const data = await res.json();
    renderResults(data);
    showToast(`Found ${data.metadata.total_resources} free resources!`, 'success');
  } catch (err) {
    showLoading(false);
    if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
      showToast('Cannot reach backend. Is the server running on port 8000?', 'error');
    } else {
      showToast(`Error: ${err.message}`, 'error');
    }
    console.error(err);
  }
}

// ─── Load sample data (no server needed) ─────────────────
async function loadSampleData() {
  showLoading(true);
  document.getElementById('results-section').style.display = 'none';

  // Try backend first; if it's offline, instantly fall back to built-in data
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 1500); // 1.5s timeout

  try {
    const res = await fetch(`${API_BASE}/api/v1/courses/sample`, { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) throw new Error(`Server error (${res.status})`);
    const data = await res.json();
    renderResults(data);
    showToast('Sample data loaded from server!', 'success');
  } catch (err) {
    clearTimeout(timeout);
    showLoading(false);
    // Backend offline → use built-in static sample immediately
    renderResults(STATIC_SAMPLE);
    document.getElementById('demo-banner').style.display = 'flex';
    showToast('Demo mode: showing built-in sample data ✓', 'info');
  }
}

// ─── Show/hide loading skeletons ─────────────────────────
function showLoading(show) {
  const loading = document.getElementById('loading-section');
  const sk = document.getElementById('sk1');

  // Duplicate skeletons for grid effect
  if (show) {
    const parent = sk.parentElement;
    parent.innerHTML = Array.from({ length: 6 }).map(() => `
      <div class="skeleton-card">
        <div class="skeleton skeleton-thumb"></div>
        <div class="skeleton-body">
          <div class="skeleton-tags">
            <div class="skeleton skeleton-tag"></div>
            <div class="skeleton skeleton-tag"></div>
          </div>
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-title-2"></div>
          <div class="skeleton skeleton-line"></div>
          <div class="skeleton skeleton-line"></div>
          <div class="skeleton skeleton-line-short"></div>
          <div class="skeleton skeleton-btn" style="margin-top:14px"></div>
        </div>
      </div>
    `).join('');
  }

  loading.style.display = show ? 'block' : 'none';
}

// ─── Render results ───────────────────────────────────────
function renderResults(data) {
  showLoading(false);

  state.allTech = data.technical_recommendations || [];
  state.allSoft = data.soft_recommendations || [];

  const meta = data.metadata || {};

  // Update stat chips
  document.getElementById('stat-total').textContent = meta.total_resources ?? (state.allTech.length + state.allSoft.length);
  document.getElementById('stat-tech').textContent = meta.technical_count ?? state.allTech.length;
  document.getElementById('stat-soft').textContent = meta.soft_count ?? state.allSoft.length;

  // Update tab counts
  document.getElementById('tech-count').textContent = state.allTech.length;
  document.getElementById('soft-count').textContent = state.allSoft.length;

  // Last updated
  if (meta.generated_at) {
    const dt = new Date(meta.generated_at);
    document.getElementById('last-updated').textContent = `Generated ${dt.toLocaleTimeString()}`;
  }

  // Demo banner
  document.getElementById('demo-banner').style.display = meta.demo_mode ? 'flex' : 'none';

  // Populate platform filter
  const platforms = new Set([
    ...state.allTech.map(r => r.platform),
    ...state.allSoft.map(r => r.platform),
  ]);
  const platformSel = document.getElementById('filter-platform');
  platformSel.innerHTML = '<option value="">All Platforms</option>' +
    [...platforms].sort().map(p => `<option value="${p}">${p}</option>`).join('');

  document.getElementById('results-section').style.display = 'block';

  applyFilters();
}

// ─── Tab switching ────────────────────────────────────────
function switchTab(tab) {
  state.currentTab = tab;
  document.getElementById('tab-tech').classList.toggle('active', tab === 'tech');
  document.getElementById('tab-soft').classList.toggle('active', tab === 'soft');
  applyFilters();
}

// ─── Filter + search + render cards ──────────────────────
function applyFilters() {
  const query = document.getElementById('search-input').value.toLowerCase();
  const difficulty = document.getElementById('filter-difficulty').value;
  const type = document.getElementById('filter-type').value;
  const platform = document.getElementById('filter-platform').value;

  const source = state.currentTab === 'tech' ? state.allTech : state.allSoft;

  const filtered = source.filter(r => {
    const matchSearch = !query || (
      (r.title || '').toLowerCase().includes(query) ||
      (r.platform || '').toLowerCase().includes(query) ||
      (r.skill || '').toLowerCase().includes(query) ||
      (r.description || '').toLowerCase().includes(query)
    );
    const matchDifficulty = !difficulty || r.difficulty === difficulty;
    const matchType = !type || r.resource_type === type;
    const matchPlatform = !platform || r.platform === platform;
    return matchSearch && matchDifficulty && matchType && matchPlatform;
  });

  document.getElementById('visible-count').textContent = filtered.length;
  document.getElementById('total-count').textContent = source.length;

  const container = document.getElementById('cards-container');

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">No resources found</div>
        <div class="empty-desc">Try adjusting your filters or search query.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(r => buildCard(r)).join('');
}

// ─── Build a single card HTML ─────────────────────────────
function buildCard(r) {
  const icon = getPlatformIcon(r.platform);
  const diffClass = {
    'Beginner': 'tag-beginner',
    'Intermediate': 'tag-intermediate',
    'Advanced': 'tag-advanced',
  }[r.difficulty] || 'tag-beginner';

  const skillTagClass = r.skill_category === 'Soft' ? 'tag-soft-skill' : 'tag-skill';

  const thumbHtml = r.thumbnail
    ? `<img src="${escHtml(r.thumbnail)}" alt="${escHtml(r.title)}" loading="lazy" onerror="this.parentElement.innerHTML=fallbackThumb('${icon}')" />`
    : fallbackThumb(icon);

  const durationMeta = r.duration
    ? `<span>${escHtml(r.duration)}</span><span class="meta-dot"></span>`
    : '';

  const sourceLabel = {
    'youtube': 'YouTube API',
    'tavily': 'Web Search',
    'sample': 'Curated',
  }[r.source] || 'Curated';

  return `
    <div class="course-card" onclick="window.open('${escHtml(r.url)}', '_blank')">
      <div class="card-glow"></div>
      <div class="card-thumb">
        ${thumbHtml}
        <div class="card-platform-badge">${icon} ${escHtml(r.platform)}</div>
        <div class="free-badge">FREE</div>
      </div>
      <div class="card-body">
        <div class="card-tags">
          <span class="tag ${skillTagClass}">${escHtml(r.skill)}</span>
          <span class="tag ${diffClass}">${escHtml(r.difficulty)}</span>
          <span class="tag tag-type">${escHtml(r.resource_type)}</span>
        </div>
        <div class="card-title">${escHtml(r.title)}</div>
        <div class="card-desc">${escHtml(r.description || '')}</div>
        <div class="card-meta">
          ${durationMeta}
          <span>${escHtml(r.resource_type)}</span>
          <span class="meta-dot"></span>
          <span>Free Access</span>
        </div>
        <div class="card-cta">
          <a class="cta-link" href="${escHtml(r.url)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">
            Start Learning
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </a>
          <span class="source-chip">${sourceLabel}</span>
        </div>
      </div>
    </div>
  `;
}

function fallbackThumb(icon) {
  return `<div class="card-thumb-placeholder"><div class="thumb-icon">${icon}</div></div>`;
}

function escHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ─── Clear all inputs ─────────────────────────────────────
function clearAll() {
  document.getElementById('inp-tech').value = '';
  document.getElementById('inp-soft').value = '';
  document.getElementById('inp-job').value = '';
  document.getElementById('inp-python-level').value = '';
  document.getElementById('inp-sql-level').value = '';
  document.querySelectorAll('.quick-chip').forEach(c => c.classList.remove('selected'));
  document.getElementById('results-section').style.display = 'none';
  document.getElementById('loading-section').style.display = 'none';
  document.getElementById('demo-banner').style.display = 'none';
  document.getElementById('stat-total').textContent = '—';
  document.getElementById('stat-tech').textContent = '—';
  document.getElementById('stat-soft').textContent = '—';
}

// ─── Static fallback sample (when backend is offline) ────
const STATIC_SAMPLE = {
  status: 'success',
  message: 'Built-in sample data (backend offline)',
  technical_recommendations: [
    { title: 'Python Tutorial for Beginners – Full Course', platform: 'YouTube – freeCodeCamp', skill: 'Python', skill_category: 'Technical', difficulty: 'Beginner', description: 'A comprehensive Python tutorial covering variables, loops, functions, OOP and more. Perfect for absolute beginners.', url: 'https://www.youtube.com/watch?v=rfscVS0vtbw', resource_type: 'Video', is_free: true, thumbnail: 'https://img.youtube.com/vi/rfscVS0vtbw/hqdefault.jpg', duration: '4.5 hours', source: 'sample' },
    { title: 'Python Tutorial – W3Schools', platform: 'W3Schools', skill: 'Python', skill_category: 'Technical', difficulty: 'Beginner', description: 'Interactive Python tutorial covering syntax, data types, conditionals, loops, and built-in functions with live examples.', url: 'https://www.w3schools.com/python/', resource_type: 'Tutorial', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'Python – GeeksforGeeks', platform: 'GeeksforGeeks', skill: 'Python', skill_category: 'Technical', difficulty: 'Intermediate', description: 'In-depth Python articles covering core language features, libraries (NumPy, Pandas), and interview problems.', url: 'https://www.geeksforgeeks.org/python-programming-language/', resource_type: 'Tutorial', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'SQL Tutorial – W3Schools', platform: 'W3Schools', skill: 'SQL', skill_category: 'Technical', difficulty: 'Beginner', description: 'Learn SQL from scratch — SELECT, WHERE, JOIN, GROUP BY, subqueries, and more with interactive exercises.', url: 'https://www.w3schools.com/sql/', resource_type: 'Tutorial', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'SQLZoo – Interactive SQL Practice', platform: 'SQLZoo', skill: 'SQL', skill_category: 'Technical', difficulty: 'Beginner', description: 'Hands-on SQL practice with real databases. Covers SELECT basics through complex JOINs and window functions.', url: 'https://sqlzoo.net/wiki/SQL_Tutorial', resource_type: 'Tutorial', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'Power BI for Beginners – Microsoft Learn', platform: 'Microsoft Learn', skill: 'Power BI', skill_category: 'Technical', difficulty: 'Beginner', description: 'Official Microsoft Learn path covering data modeling, DAX, and report building.', url: 'https://learn.microsoft.com/en-us/training/powerplatform/power-bi', resource_type: 'Course', is_free: true, thumbnail: null, duration: '8 hours', source: 'sample' },
    { title: 'Machine Learning – Kaggle Learn', platform: 'Kaggle Learn', skill: 'Machine Learning', skill_category: 'Technical', difficulty: 'Beginner', description: 'Free hands-on ML course: model validation, overfitting, random forests and more with Kaggle notebooks.', url: 'https://www.kaggle.com/learn/intro-to-machine-learning', resource_type: 'Course', is_free: true, thumbnail: null, duration: '3 hours', source: 'sample' },
    { title: 'Web Development Full Course – freeCodeCamp', platform: 'freeCodeCamp', skill: 'Web Development', skill_category: 'Technical', difficulty: 'Beginner', description: 'Complete web development curriculum covering HTML, CSS, JavaScript, responsive design and React.', url: 'https://www.freecodecamp.org/learn/', resource_type: 'Course', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'SQL for Data Science – Kaggle Learn', platform: 'Kaggle Learn', skill: 'SQL', skill_category: 'Technical', difficulty: 'Beginner', description: 'Free micro-course by Kaggle covering SQL basics for data science including BigQuery.', url: 'https://www.kaggle.com/learn/intro-to-sql', resource_type: 'Course', is_free: true, thumbnail: null, duration: '3 hours', source: 'sample' },
    { title: 'Power BI Full Course – YouTube', platform: 'YouTube', skill: 'Power BI', skill_category: 'Technical', difficulty: 'Beginner', description: 'Complete Power BI tutorial from dashboard creation to publishing and sharing reports.', url: 'https://www.youtube.com/watch?v=TmhQCQr_4GE', resource_type: 'Video', is_free: true, thumbnail: 'https://img.youtube.com/vi/TmhQCQr_4GE/hqdefault.jpg', duration: '6 hours', source: 'sample' },
    { title: 'Machine Learning Specialization – Andrew Ng (Audit)', platform: 'Coursera (Audit Free)', skill: 'Machine Learning', skill_category: 'Technical', difficulty: 'Intermediate', description: "World-famous ML course by Andrew Ng. Audit for free.", url: 'https://www.coursera.org/specializations/machine-learning-introduction', resource_type: 'Course', is_free: true, thumbnail: null, duration: '~3 months', source: 'sample' },
    { title: 'Data Analytics – Google (via Coursera Audit)', platform: 'Coursera (Audit Free)', skill: 'Data Analytics', skill_category: 'Technical', difficulty: 'Beginner', description: "Google's official data analytics certificate. Covers spreadsheets, SQL, R, and Tableau. Audit for free.", url: 'https://www.coursera.org/professional-certificates/google-data-analytics', resource_type: 'Course', is_free: true, thumbnail: null, duration: '6 months', source: 'sample' },
  ],
  soft_recommendations: [
    { title: 'Communication Skills – NPTEL', platform: 'NPTEL', skill: 'Communication', skill_category: 'Soft', difficulty: 'Beginner', description: 'Free NPTEL course on English communication for technical professionals.', url: 'https://nptel.ac.in/courses/109/104/109104093/', resource_type: 'Course', is_free: true, thumbnail: null, duration: '12 weeks', source: 'sample' },
    { title: 'Business English Communication – SWAYAM', platform: 'SWAYAM', skill: 'Communication', skill_category: 'Soft', difficulty: 'Beginner', description: 'SWAYAM course on business communication and professional English.', url: 'https://swayam.gov.in/nd1_noc19_hs45/preview', resource_type: 'Course', is_free: true, thumbnail: null, duration: '8 weeks', source: 'sample' },
    { title: 'Leadership & Management – TCS iON', platform: 'TCS iON', skill: 'Leadership', skill_category: 'Soft', difficulty: 'Beginner', description: 'Free TCS iON course on leadership styles, team management, and decision making.', url: 'https://learning.tcsionhub.in/hub/national/', resource_type: 'Course', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'Problem Solving – GeeksforGeeks', platform: 'GeeksforGeeks', skill: 'Problem Solving', skill_category: 'Soft', difficulty: 'Beginner', description: 'Articles and practice problems focused on analytical thinking and structured problem-solving.', url: 'https://www.geeksforgeeks.org/puzzles/', resource_type: 'Tutorial', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'Time Management – NPTEL', platform: 'NPTEL', skill: 'Time Management', skill_category: 'Soft', difficulty: 'Beginner', description: 'NPTEL lectures on productivity, prioritization and goal setting.', url: 'https://nptel.ac.in/courses/110/106/110106061/', resource_type: 'Course', is_free: true, thumbnail: null, duration: '4 weeks', source: 'sample' },
    { title: 'Public Speaking – TED-Ed', platform: 'YouTube', skill: 'Public Speaking', skill_category: 'Soft', difficulty: 'Beginner', description: 'TED-Ed videos on overcoming public speaking anxiety and confident delivery.', url: 'https://www.youtube.com/playlist?list=PLJicmE8fK0EiEzttYMD1zYkT-SmNf323z', resource_type: 'Playlist', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'Interview Skills & Career Readiness – TCS iON', platform: 'TCS iON', skill: 'Interview Skills', skill_category: 'Soft', difficulty: 'Beginner', description: 'TCS iON free course on interview preparation, resume writing, and professional etiquette.', url: 'https://learning.tcsionhub.in/hub/national/', resource_type: 'Course', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
    { title: 'Leadership Skills – Simon Sinek (YouTube)', platform: 'YouTube', skill: 'Leadership', skill_category: 'Soft', difficulty: 'Beginner', description: "Simon Sinek's leadership talks covering trust, purpose, and team culture.", url: 'https://www.youtube.com/c/SimonSinek', resource_type: 'Playlist', is_free: true, thumbnail: null, duration: 'Self-paced', source: 'sample' },
  ],
  metadata: {
    total_resources: 20,
    technical_count: 12,
    soft_count: 8,
    skills_covered: ['Python', 'SQL', 'Power BI', 'Machine Learning', 'Web Development', 'Data Analytics', 'Communication', 'Leadership', 'Problem Solving', 'Time Management', 'Public Speaking', 'Interview Skills'],
    demo_mode: true,
    generated_at: new Date().toISOString(),
  },
};
