function imgUpload() {
  let imgUpload = document.querySelectorAll('.img-upload');
  let preview = document.getElementById('img-preview');
  
  imgUpload.forEach(elem => {
    elem.addEventListener('change', e => {
      preview.src = '';
      let file = elem.files[0];
      if (file.size > 1024 * 1024) {
        elem.value = null;
        let modal = new bootstrap.Modal('#upload-err', {});
        modal.show();
      }
      else {
        preview.src = URL.createObjectURL(file);
      }
    });
  });  
}


function previewPost() {
  let converter = new showdown.Converter();
  let postBody = document.getElementById('post-body');
  let postTitle  = document.getElementById('post-title');
  let previewBody = document.getElementById('preview-post').getElementsByClassName('modal-body')[0];
  let previewHeader = document.getElementById('preview-post').getElementsByClassName('modal-title')[0];
  let html = converter.makeHtml(postBody.value);
  previewHeader.innerHTML = postTitle.value;
  previewBody.innerHTML = html;
  let modal = new bootstrap.Modal('#preview-post', {});
  modal.show();
}
