// chat
function scrollToBottom() {
  const container = document.getElementById("chat-container");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

// Scroll saat load pertama & setelah HTMX request selesai
document.addEventListener("DOMContentLoaded", scrollToBottom);
document.body.addEventListener("htmx:afterSwap", scrollToBottom);

// scan
// Fungsi Preview Gambar saat dipilih
function previewImage(input) {
  const preview = document.getElementById("image-preview");
  const placeholder = document.getElementById("placeholder-content");
  const dropzone = document.getElementById("dropzone");

  if (input.files && input.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.classList.remove("hidden");

      // Sedikit delay agar transisi opacity jalan
      setTimeout(() => {
        preview.classList.remove("opacity-0");
      }, 10);

      placeholder.classList.add("opacity-0"); // Sembunyikan placeholder text
      dropzone.classList.add("border-teal-500"); // Ubah border jadi teal
    };

    reader.readAsDataURL(input.files[0]);
  }
}

// Fungsi Validasi & Show Loading
function showLoading() {
  const fileInput = document.getElementById("id_receipt_image");

  // Hanya munculkan loading jika file sudah dipilih
  if (fileInput.files.length > 0) {
    const overlay = document.getElementById("loadingOverlay");
    overlay.classList.remove("hidden");
    overlay.classList.add("flex"); // Agar centering jalan
  } else {
    // Optional: Alert sederhana jika lupa pilih file
    // alert("Pilih foto nota dulu ya bos!");
  }
}

// manual input
document.addEventListener("DOMContentLoaded", (event) => {
  const dateInput = document.querySelector('input[type="date"]');
  if (dateInput && !dateInput.value) {
    dateInput.valueAsDate = new Date();
  }
});

// Fungsi Show Loading untuk Manual Input
window.showManualInputLoading = function() {
  console.log("showManualInputLoading called");
  const form = document.querySelector("form");
  
  // Cek validasi form HTML5 (required, type, dll)
  if (form && !form.checkValidity()) {
    console.log("Form is invalid");
    // Biarkan browser menampilkan pesan error bawaan
    return;
  }

  const overlay = document.getElementById("loadingOverlayManualInput");
  if (overlay) {
    overlay.classList.remove("hidden");
    overlay.classList.add("flex");
  } else {
    console.error("loadingOverlayManualInput not found");
  }
};
