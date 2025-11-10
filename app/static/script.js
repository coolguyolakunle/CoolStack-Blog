document.addEventListener("DOMContentLoaded", () => {
  let lastScrollTop = 0;
  const navbar = document.getElementById("navBar");
  const scrollThreshold = 10;

  window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    if (Math.abs(currentScroll - lastScrollTop) <= scrollThreshold) return;

    if (currentScroll > lastScrollTop && currentScroll > navbar.offsetHeight) {
      navbar.style.transform = "translateY(-100%)";
      navbar.style.transition = "transform 0.4s ease";
    } else {
      navbar.style.transform = "translateY(0)";
      navbar.style.transition = "transform 0.4s ease";
    }
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
  });

  // for like button
    document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("like-btn")) {
      const postId = e.target.dataset.postId;
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

      try {
        const res = await fetch(`/like/${postId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
          }
        });

        if (!res.ok) throw new Error("Network response was not ok");
        const data = await res.json();

        const likeCount = document.querySelector(`#like-count-${postId}`);
        if (likeCount) likeCount.textContent = data.like_count;

        e.target.classList.toggle("liked", data.liked);
      } catch (err) {
        console.error("Error:", err);
      }
    }
  });

  // search results
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Remove active from all
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      // Activate current
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });


  // COMMENT MODAL 
  const commentModal = document.getElementById("commentModal");
  const closeCommentBtn = commentModal?.querySelector(".close");
  const commentBtns = document.querySelectorAll(".comment-btn");
  const commentSection = document.getElementById("commentSection");

  commentBtns.forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const postId = btn.dataset.postId;

      try {
        const response = await fetch(`/comments/${postId}`, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("Failed to load comments");
        const html = await response.text();
        commentSection.innerHTML = html;
        commentModal.style.display = "block";
      } catch (err) {
        console.error(err);
        alert("Error loading comments. Please try again.");
      }
    });
  });

  closeCommentBtn && (closeCommentBtn.onclick = () => (commentModal.style.display = "none"));
  window.onclick = (e) => {
    if (e.target === commentModal) commentModal.style.display = "none";
  };

  // COMMENT SUBMIT (AJAX)
  document.addEventListener("submit", async (e) => {
    if (e.target.id === "commentForm") {
      e.preventDefault();
      const form = e.target;
      const data = new FormData(form);

      try {
        const response = await fetch(form.action, { method: "POST", body: data });
        const html = await response.text();
        document.getElementById("commentSection").innerHTML = html;
      } catch (err) {
        console.error(err);
        alert("Error sending comment. Please refresh and try again.");
      }
    }
  });

  // LOGIN / SIGNUP MODALS
  const loginModal = document.getElementById("loginModal");
  const signupModal = document.getElementById("signupModal");

  const loginBtn = document.querySelector(".login_btn");
  const signupBtn = document.querySelector(".signup_btn");
  const closeLogin = document.getElementById("closeLogin");
  const closeSignup = document.getElementById("closeSignup");
  const switchToSignup = document.getElementById("switchToSignup");
  const switchToLogin = document.getElementById("switchToLogin");

  loginBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    loginModal.style.display = "block";
  });

  signupBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    signupModal.style.display = "block";
  });

  closeLogin?.addEventListener("click", () => (loginModal.style.display = "none"));
  closeSignup?.addEventListener("click", () => (signupModal.style.display = "none"));

  switchToSignup?.addEventListener("click", (e) => {
    e.preventDefault();
    loginModal.style.display = "none";
    signupModal.style.display = "block";
  });

  switchToLogin?.addEventListener("click", (e) => {
    e.preventDefault();
    signupModal.style.display = "none";
    loginModal.style.display = "block";
  });

  window.addEventListener("click", (e) => {
    if (e.target === loginModal) loginModal.style.display = "none";
    if (e.target === signupModal) signupModal.style.display = "none";
  });

  // CREATE POST MODAL
  const openPostBtn = document.getElementById("openCreatePost");
  const postModal = document.getElementById("createPostModal");
  const closePostBtn = document.getElementById("closeCreatePost");
  const postContent = document.getElementById("createPostContent");

  if (openPostBtn) {
    openPostBtn.addEventListener("click", (e) => {
      e.preventDefault();
      fetch("/create_post")
        .then((response) => {
          if (!response.ok) throw new Error("Error loading form.");
          return response.text();
        })
        .then((html) => {
          postContent.innerHTML = html;
          postModal.style.display = "flex";
        })
        .catch((err) => {
          postContent.innerHTML = "<p style='color:red;'>Error loading form. Please try again.</p>";
        });
    });
  }

  if (closePostBtn) {
    closePostBtn.addEventListener("click", () => (postModal.style.display = "none"));
  }

  window.addEventListener("click", (e) => {
    if (e.target === postModal) postModal.style.display = "none";
  });

  // HANDLE CREATE POST SUBMISSION (AJAX)
  document.addEventListener("submit", async function (e) {
    if (e.target.matches(".create-post-form")) {
      e.preventDefault();

      const form = e.target;
      const modal = document.getElementById("createPostModal");
      const formData = new FormData(form);

      try {
        const response = await fetch("/create_post", {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        if (!response.ok) throw new Error("Error creating post.");

        const data = await response.json();

        if (data.success) {
          showFlashMessage("Post created successfully!", "success");
          modal.style.display = "none";
          form.reset();
        } else {
          showFlashMessage(data.message || "Something went wrong.", "error");
        }
      } catch (error) {
        showFlashMessage("Error creating post. Please try again.", "error");
      }
    }
  });

  //  DELETE POST CONFIRMATION MODAL 
  const deleteButtons = document.querySelectorAll(".delete");
  let formToSubmit = null;

  // Create modal dynamically if it doesn’t exist
  let deleteModal = document.getElementById("deleteConfirmModal");
  if (!deleteModal) {
    deleteModal = document.createElement("div");
    deleteModal.id = "deleteConfirmModal";
    deleteModal.className = "modal-overlay";
    deleteModal.style.display = "none";
    deleteModal.innerHTML = `
      <div class="modal-content">
        <h3>Delete Post?</h3>
        <p>This action cannot be undone.</p>
        <div class="modal-buttons">
          <button id="confirmDeleteBtn" class="confirm-delete">Yes, delete</button>
          <button id="cancelDeleteBtn" class="cancel-delete">Cancel</button>
        </div>
      </div>
    `;
    document.body.appendChild(deleteModal);
  }

  const confirmBtn = deleteModal.querySelector("#confirmDeleteBtn");
  const cancelBtn = deleteModal.querySelector("#cancelDeleteBtn");

  deleteButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      formToSubmit = btn.closest("form");
      deleteModal.style.display = "flex";
      deleteModal.style.animation = "fadeIn 0.3s ease forwards";
    });
  });

  confirmBtn.addEventListener("click", () => {
    if (formToSubmit) {
      formToSubmit.submit();
      deleteModal.style.display = "none";
    }
  });

  cancelBtn.addEventListener("click", () => {
    deleteModal.style.animation = "fadeOut 0.3s ease forwards";
    setTimeout(() => (deleteModal.style.display = "none"), 300);
    formToSubmit = null;
  });

  window.addEventListener("click", (e) => {
    if (e.target === deleteModal) {
      deleteModal.style.animation = "fadeOut 0.3s ease forwards";
      setTimeout(() => (deleteModal.style.display = "none"), 300);
      formToSubmit = null;
    }
  });


  // FLASH MESSAGE HELPER 
  function showFlashMessage(message, category) {
    const flash = document.createElement("div");
    flash.className = `flash ${category}`;
    flash.textContent = message;
    document.body.appendChild(flash);

    setTimeout(() => {
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 500);
    }, 3000);
  }

  // Convert post date to "time ago" style
  function timeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const seconds = Math.floor((now - past) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    const weeks = Math.floor(days / 7);
    if (weeks < 4) return `${weeks}w ago`;
    const months = Math.floor(days / 30);
    if (months < 12) return `${months}mo ago`;
    const years = Math.floor(days / 365);
    return `${years}y ago`;
  }

  // Apply it to all .date spans
  function updateTimeAgo() {
    document.querySelectorAll(".date").forEach((el) => {
      const time = el.dataset.time;
      if (time) el.textContent = timeAgo(time);
    });
  }

  // Run once on page load, then update every minute
  updateTimeAgo();
  setInterval(updateTimeAgo, 60000);

  document.querySelectorAll('.video-container').forEach(container => {
    const video = container.querySelector('video');
    const overlay = container.querySelector('.play-overlay');

    overlay.addEventListener('click', () => {
      video.play();
    });

    video.addEventListener('play', () => {
      container.classList.add('playing');
    });

    video.addEventListener('pause', () => {
      container.classList.remove('playing');
    });
  });

});

//  AUTO-HIDE FLASK FLASH MESSAGES 
document.addEventListener("DOMContentLoaded", function () {
  const flashMessages = document.querySelectorAll(".flash");
  flashMessages.forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.6s ease";
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 600);
    }, 4000);
  });
});
