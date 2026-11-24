'use strict';

const all = document.querySelector('#all');
const autoPlay = !matchMedia('(prefers-reduced-motion: reduce)').matches;
const players = [...document.querySelectorAll('.card')].map(card => ({
  video: card.querySelector('video'),
  button: card.querySelector('.play'),
  name: card.querySelector('h2').textContent,
  wanted: autoPlay,
  visible: false,
}));

function refresh() {
  for (const {video, button, name} of players) {
    const action = video.paused ? '播放' : '暂停';
    button.textContent = action;
    button.setAttribute('aria-label', action + name);
  }
  all.textContent = players.some(({wanted}) => wanted) ? '暂停全部' : '播放全部';
}

async function play(video) {
  try {
    await video.play();
  } catch {
    refresh();
  }
}

const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
    const player = players.find(({video}) => video === entry.target);
    player.visible = entry.isIntersecting;
    sync(player);
  }
});

function sync({video, visible, wanted}) {
  if (wanted && visible && !document.hidden) play(video);
  else video.pause();
}

for (const player of players) {
  const {video,button}=player;
  video.controls = false;
  button.hidden = false;
  button.addEventListener('click', () => {
    player.wanted=video.paused;
    sync(player);
    refresh();
  });
  video.addEventListener('play', refresh);
  video.addEventListener('pause', refresh);
  video.addEventListener('error', () => {
    button.textContent = '无法播放';
    button.disabled = true;
    video.controls = true;
  });
  observer.observe(video);
}

all.hidden = false;
all.addEventListener('click', () => {
  const wanted=!players.some(player=>player.wanted);
  for (const player of players) {
    player.wanted=wanted;
    sync(player);
  }
  refresh();
});

document.addEventListener('visibilitychange',()=>players.forEach(sync));
refresh();
