// small admin interactivity
document.addEventListener('DOMContentLoaded', function(){
  // highlight current nav item
  const path = window.location.pathname;
  document.querySelectorAll('.admin-sidebar .nav-item').forEach(a => {
    if(path.startsWith(a.getAttribute('href'))){
      a.classList.add('active');
      a.style.background = 'rgba(255,255,255,0.03)';
    }
  });
});
