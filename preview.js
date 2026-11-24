'use strict';

const all = document.querySelector('#all');
const players = [...document.querySelectorAll('.card')].map(card => ({
  video: card.querySelector('video'),
  button: card.querySelector('.play'),
  name: card.querySelector('h2').textContent,
}));

function refresh() {
  for (const {video, button, name} of players) {
    const action = video.paused ? '播放' : '暂停';
    button.textContent = action;
    button.setAttribute('aria-label', action + name);
  }
  all.textContent = players.every(({video}) => video.paused) ? '播放全部' : '暂停全部';
}

async function play(video) {
  try {
    await video.play();
  } catch {
    refresh();
  }
}

for (const {video, button} of players) {
  video.controls = false;
  button.hidden = false;
  button.addEventListener('click', () => {
    if (video.paused) play(video);
    else video.pause();
  });
  video.addEventListener('play', refresh);
  video.addEventListener('pause', refresh);
  video.addEventListener('error', () => {
    button.textContent = '无法播放';
    button.disabled = true;
    video.controls = true;
  });
}

all.hidden = false;
all.addEventListener('click', () => {
  if (players.every(({video}) => video.paused)) {
    for (const {video} of players) play(video);
  } else {
    for (const {video} of players) video.pause();
  }
});

if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
  for (const {video} of players) play(video);
}
