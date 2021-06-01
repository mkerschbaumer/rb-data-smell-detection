// https://jsfiddle.net/xg1kwv67/

document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('.file-droppable').forEach(function(droppable) {
    var originalText = droppable.querySelector('div').innerHTML;
    var input = droppable.querySelector('input');
    var fileChanged = function() {
      var files = input.files;
      if (files.length) {
        droppable.querySelector('span').style.display = 'block';
        droppable.querySelector('div').innerHTML = '';
				for (var i = 0; i < files.length; i++) {
					droppable.querySelector('div').innerHTML += files[i].name + '<br>';
        }
        droppable.classList.add('filled');
      } else {
        droppable.querySelector('div').innerHTML = originalText;
        droppable.classList.remove('filled');
        droppable.querySelector('span').style.display = 'none';
      }
    };
    input.addEventListener('change', fileChanged);
    fileChanged(input);
    droppable.querySelector('span').addEventListener('click', function() {
		  input.value = '';
	    fileChanged(input);
    });
  });
});