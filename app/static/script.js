// script.js — clean, modular, fault-tolerant version
document.addEventListener("DOMContentLoaded", () => {
  console.log("Script loaded ✅");

  // Always show page immediately after DOM is ready
  document.body.classList.remove("page-loading");

  document.addEventListener("click", (e) => {
    const a = e.target.closest("a");
    if (!a) return;

    const href = a.getAttribute("href");
    if (!href || href.startsWith("#")) return;
    if (a.target === "_blank") return;
    if (a.hasAttribute("download")) return;
    if (e.ctrlKey || e.metaKey) return;

    const url = new URL(a.href, window.location.href);
    if (url.origin !== window.location.origin) return;

    e.preventDefault();
    document.body.classList.add("page-loading");

    setTimeout(() => {
      window.location.href = a.href;
    }, 220);
  });



  function showFlash(message, type = "success") {
    const flash = document.getElementById("flashMessage");
    if (!flash) return;

    flash.textContent = message;
    flash.className = "";        // remove all classes
    flash.classList.add(type, "show");

    // auto-hide after 3 seconds
    setTimeout(() => {
      flash.classList.remove("show");
    }, 3000);
  }


  /* ---------------------- HELPERS ---------------------- */
  const safeQuery = (sel) => document.querySelector(sel);
  const safeQueryAll = (sel) => Array.from(document.querySelectorAll(sel));
  const getMetaCSRF = () => document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || null;
  const sleep = (ms) => new Promise(res => setTimeout(res, ms));

  /* ------------------ NAVBAR: HIDE ON SCROLL ------------------ */
  (function navbarScroll() {
    const navbar = document.getElementById("navBar");
    if (!navbar) return;
    let lastScrollTop = 0;
    const threshold = 10;
    window.addEventListener("scroll", () => {
      try {
        const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        if (Math.abs(currentScroll - lastScrollTop) <= threshold) return;
        if (currentScroll > lastScrollTop && currentScroll > navbar.offsetHeight) {
          navbar.style.transform = "translateY(-100%)";
        } else {
          navbar.style.transform = "translateY(0)";
        }
        navbar.style.transition = "transform 0.4s ease";
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
      } catch (err) {
        console.error("Navbar scroll error:", err);
      }
    });
  })();

  /* ------------------ HAMBURGER / OVERLAY ------------------ */
  (function hamburgerOverlay() {
    const hamburger = document.getElementById("hamburger");
    const navOverlay = document.getElementById("navOverlay");
    if (!hamburger || !navOverlay) return;

    const overlayMenu = navOverlay.querySelector(".menu");
    const overlayDropdown = navOverlay.querySelector(".overlay-dropdown");
    const overlayDropBtn = overlayDropdown?.querySelector(".overlay-dropbtn");

    const openOverlay = () => {
      hamburger.classList.add("active");
      navOverlay.classList.add("show");
      document.body.classList.add("menu-open"); // ✅ stop background scroll
    };

    const closeOverlay = () => {
      navOverlay.classList.remove("show");
      hamburger.classList.remove("active");
      overlayDropdown?.classList.remove("open");
      document.body.classList.remove("menu-open"); // ✅ allow scroll again
    };

    hamburger.addEventListener("click", () => {
      const isOpen = navOverlay.classList.contains("show");
      if (isOpen) closeOverlay();
      else openOverlay();
    });

    navOverlay.addEventListener("click", (e) => {
      if (!overlayMenu?.contains(e.target)) closeOverlay();
    });

    overlayDropBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      overlayDropdown.classList.toggle("open");
    });

    overlayMenu?.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", closeOverlay);
    });

    // ✅ If user scrolls while overlay is open, keep it open and keep blur
    window.addEventListener("scroll", () => {
      if (navOverlay.classList.contains("show")) {
        document.body.classList.add("menu-open");
      }
    }, { passive: true });
  })();



  /* ------------------ EVENT DELEGATION: GLOBAL CLICK HANDLER ------------------ */
  // Used for like buttons (delegated), can extend further
  document.addEventListener("click", async (e) => {
    // LIKE BUTTON (delegated)
    const likeBtn = e.target.closest(".like-btn");
    if (likeBtn) {
      e.preventDefault();
      const postId = likeBtn.dataset.postId;
      if (!postId) return console.warn("like-btn missing data-post-id");
      try {
        const csrf = getMetaCSRF();
        const res = await fetch(`/main/like/${postId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(csrf ? { "X-CSRFToken": csrf } : {})
          }
        });
        if (!res.ok) throw new Error("Network response not OK");
        const json = await res.json();
        // update UI
        const likeCountEl = document.getElementById(`like-count-${postId}`);
        if (likeCountEl && typeof json.like_count !== "undefined") likeCountEl.textContent = json.like_count;
        likeBtn.classList.toggle("liked", !!json.liked);
      } catch (err) {
        console.error("Like error:", err);
      }
      return;
    }

    // Other delegated click behaviors can be added here...
  });

  /* ------------------ SEARCH TABS ------------------ */
  (function searchTabs() {
    const tabButtons = safeQueryAll(".tab-button");
    const tabContents = safeQueryAll(".tab-content");
    if (!tabButtons.length || !tabContents.length) return;
    tabButtons.forEach(button => {
      button.addEventListener("click", (e) => {
        e.preventDefault();
        tabButtons.forEach(b => b.classList.remove("active"));
        tabContents.forEach(c => c.style.display = "none");
        button.classList.add("active");
        const tabId = button.textContent.trim().toLowerCase();
        const target = document.getElementById(tabId);
        if (target) target.style.display = "block";
      });
    });
  })();

  /* ------------------ FOLLOW / UNFOLLOW BUTTONS ------------------ */
  (function followButtons() {
    const buttons = safeQueryAll(".follow-btn");
    if (!buttons.length) return;
    buttons.forEach(button => {
      button.addEventListener("click", async () => {
        const userId = button.dataset.userId;
        if (!userId) return console.warn("follow-btn missing data-user-id");
        try {
          const csrf = getMetaCSRF();
          const res = await fetch(`/main/follow/${userId}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(csrf ? { "X-CSRFToken": csrf } : {})
            }
          });
          if (!res.ok) throw new Error("Network error");
          const json = await res.json();
          if (json.status === "followed") {
            button.textContent = "Unfollow";
            button.classList.remove("btn-primary");
            button.classList.add("btn-danger");
          } else if (json.status === "unfollowed") {
            button.textContent = "Follow";
            button.classList.remove("btn-danger");
            button.classList.add("btn-primary");
          } else {
            alert(json.message || "Error following/unfollowing. Please refresh and try again.");
          }
        } catch (err) {
          console.error("Follow error:", err);
          alert("Error following/unfollowing. Please refresh and try again.");
        }
      });
    });
  })();

  /* ------------------ COMMENT MODAL + LOAD ------------------ */
  (function commentModal() {
    const commentModal = document.getElementById("commentModal");
    const commentSection = document.getElementById("commentSection");
    const commentBtns = safeQueryAll(".comment-btn");
    if (!commentModal || !commentSection || !commentBtns.length) return;

    commentBtns.forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.preventDefault();
        const postId = btn.dataset.postId;
        if (!postId) return console.warn("comment-btn missing data-post-id");
        try {
          const res = await fetch(`/main/comments/${postId}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
          });
          if (!res.ok) throw new Error("Failed to load comments");
          const html = await res.text();
          commentSection.innerHTML = html;
          commentModal.style.display = "block";
        } catch (err) {
          console.error("Load comments error:", err);
          alert("Error loading comments. Please try again.");
        }
      });
    });

    const closeBtn = commentModal.querySelector(".close");
    closeBtn?.addEventListener("click", () => { commentModal.style.display = "none"; });
    window.addEventListener("click", (e) => { if (e.target === commentModal) commentModal.style.display = "none"; });
  })();

  /* ------------------ COMMENT SUBMISSION (AJAX) ------------------ */
  (function commentSubmit() {
    document.addEventListener("submit", async (e) => {
      if (e.target && e.target.id === "commentForm") {
        e.preventDefault();
        const form = e.target;
        const data = new FormData(form);
        try {
          const res = await fetch(form.action, { method: "POST", body: data });
          if (!res.ok) throw new Error("Network error submitting comment");
          const html = await res.text();
          const commentSection = document.getElementById("commentSection");
          if (commentSection) commentSection.innerHTML = html;
        } catch (err) {
          console.error("Comment submit error:", err);
          alert("Error sending comment. Please refresh and try again.");
        }
      }
    });
  })();

  /* ------------------ LOGIN / SIGNUP MODALS + AJAX FORMS ------------------ */
  (function authModals() {
    const loginModal = document.getElementById("loginModal");
    const signupModal = document.getElementById("signupModal");
    const loginBtns = safeQueryAll(".login_btn");
    const signupBtns = safeQueryAll(".signup_btn");
    const closeLogin = document.getElementById("closeLogin");
    const closeSignup = document.getElementById("closeSignup");
    const switchToSignup = document.getElementById("switchToSignup");
    const switchToLogin = document.getElementById("switchToLogin");

    // open / close only if modals exist
    loginBtns.forEach(btn => btn.addEventListener("click", (e) => {
      e.preventDefault();
      loginModal?.classList.add("show");
    }));
    signupBtns.forEach(btn => btn.addEventListener("click", (e) => {
      e.preventDefault();
      signupModal?.classList.add("show");
    }));

    closeLogin?.addEventListener("click", () => loginModal?.classList.remove("show"));
    closeSignup?.addEventListener("click", () => signupModal?.classList.remove("show"));

    switchToSignup?.addEventListener("click", (e) => {
      e.preventDefault();
      loginModal?.classList.remove("show");
      signupModal?.classList.add("show");
    });
    switchToLogin?.addEventListener("click", (e) => {
      e.preventDefault();
      signupModal?.classList.remove("show");
      loginModal?.classList.add("show");
    });

    window.addEventListener("click", (e) => {
      if (e.target === loginModal) loginModal?.classList.remove("show");
      if (e.target === signupModal) signupModal?.classList.remove("show");
    });

    // AJAX form submit helper
    const attachAjaxForm = (modalEl) => {
      if (!modalEl) return;
      const form = modalEl.querySelector("form");
      if (!form) return;
      form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        try {
          const formData = new FormData(form);
          const res = await fetch(form.action, {
            method: form.method || "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            body: formData
          });
          if (!res.ok) throw new Error("Network error");
          const json = await res.json();

          // ensure a container for messages
          let msgContainer = modalEl.querySelector(".flash-container");
          if (!msgContainer) {
            msgContainer = document.createElement("div");
            msgContainer.className = "flash-container";
            modalEl.querySelector(".login_modal_content, .signup_modal_content")?.prepend(msgContainer);
          }
          msgContainer.innerHTML = "";

          if (json.success) {
            const msg = document.createElement("div");
            msg.className = "flash-message success";
            msg.textContent = json.message || "Success";
            msgContainer.appendChild(msg);

            // 👇 redirect user if redirect_url provided
            if (json.redirect_url) {
              setTimeout(() => {
                window.location.href = json.redirect_url;
              }, 1000); // small delay so user sees the success message
            } else {
              await sleep(1200);
              modalEl.classList.remove("show");
            }
          }
          else {
            if (json.errors) {
              Object.entries(json.errors).forEach(([field, msgs]) => {
                msgs.forEach(m => {
                  const div = document.createElement("div");
                  div.className = "flash-message danger";
                  div.textContent = `${field}: ${m}`;
                  msgContainer.appendChild(div);
                });
              });
            } else if (json.message) {
              const div = document.createElement("div");
              div.className = "flash-message danger";
              div.textContent = json.message;
              msgContainer.appendChild(div);
            }
          }
        } catch (err) {
          console.error("Auth form error:", err);
        }
      });
    };

    // attach if modals exist now (in case forms were rendered server-side)
    attachAjaxForm(loginModal);
    attachAjaxForm(signupModal);
  })();

  /* ------------------ CREATE POST MODAL (LOAD FORM + SUBMIT) ------------------ */
  (function createPostModal() {
    const postModal = document.getElementById("createPostModal");
    const postContent = document.getElementById("createPostContent");
    const closePostBtn = document.getElementById("closeCreatePost");
    const openButtons = document.querySelectorAll(".openCreatePostNav, #openCreatePostNav");
    if (!openButtons.length || !postModal || !postContent) return;

    // Correct URL for your blueprint (main)
    const CREATE_POST_URL = "/main/create_post";

    openButtons.forEach(btn => 
      btn.addEventListener("click", async (e) => {
        e.preventDefault();

        try {
          const res = await fetch(CREATE_POST_URL, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
            credentials: "same-origin"
          });

          if (!res.ok) throw new Error("Error loading form");

          const html = await res.text();
          postContent.innerHTML = html;
          postModal.style.display = "flex";

          // Fetch the form inside the returned HTML
          const form = postContent.querySelector("form.create-post-form");

          if (form) {
            form.addEventListener("submit", async (ev) => {
                ev.preventDefault();

                const fd = new FormData(form);

                try {
                    const r = await fetch(CREATE_POST_URL, {
                      method: "POST",
                      body: fd,
                      headers: { "X-Requested-With": "XMLHttpRequest" },
                      credentials: "same-origin"
                    });

                    if (!r.ok) throw new Error("Error creating post");

                    const json = await r.json();

                    if (json.success) {
                      showFlash(json.message || "Post created successfully!", "success");
                      postModal.style.display = "none";
                      form.reset();
                    } else {
                      showFlash("Error creating post", "error");
                    }
                } catch (err) {
                    console.error("Submit error:", err);
                    alert("Error submitting post. Try again.");
                }
            });
          }

        } catch (err) {
            console.error("Load error:", err);
            postContent.innerHTML = "<p style='color:red;'>Error loading form. Please try again.</p>";
        }
    })
  );

    closePostBtn?.addEventListener("click", () => postModal.style.display = "none");

    window.addEventListener("click", (e) => {
      if (e.target === postModal) postModal.style.display = "none";
    });
  })();



  /* ------------------ DELETE CONFIRM MODAL ------------------ */
  (function deleteConfirm() {
    const deleteModal = document.getElementById("deleteConfirmModal");
    const confirmBtn = document.getElementById("confirmDeleteBtn");
    const cancelBtn = document.getElementById("cancelDeleteBtn");

    if (!deleteModal || !confirmBtn || !cancelBtn) return;

    let formToSubmit = null;

    // Open modal when any delete button is clicked
    document.addEventListener("click", (e) => {
      const delBtn = e.target.closest("button.delete");
      if (!delBtn) return;

      e.preventDefault();
      formToSubmit = delBtn.closest("form.delete-post-form");
      if (!formToSubmit) return;

      deleteModal.classList.add("show");
      deleteModal.setAttribute("aria-hidden", "false");
      document.body.classList.add("modal-open");
    });

    // Confirm delete
    confirmBtn.addEventListener("click", () => {
      if (formToSubmit) formToSubmit.submit();
    });

    // Cancel delete
    cancelBtn.addEventListener("click", closeModal);

    // Click outside content closes modal
    deleteModal.addEventListener("click", (e) => {
      if (e.target === deleteModal) closeModal();
    });

    // ESC closes modal
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && deleteModal.classList.contains("show")) {
        closeModal();
      }
    });

    function closeModal() {
      deleteModal.classList.remove("show");
      deleteModal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("modal-open");
      formToSubmit = null;
    }
  })();

  /* ------------------ FLASH MESSAGE HELPER & AUTO-HIDE ------------------ */
  function showFlashMessage(message, category = "info") {
    const flash = document.createElement("div");
    flash.className = `flash ${category}`;
    flash.textContent = message;
    document.body.appendChild(flash);
    // auto-hide
    setTimeout(() => { flash.style.opacity = "0"; setTimeout(() => flash.remove(), 500); }, 3000);
  }

  (function autoHideExistingFlash() {
    const flashes = safeQueryAll(".flash");
    if (!flashes.length) return;
    flashes.forEach((flash) => {
      setTimeout(() => {
        flash.style.transition = "opacity 0.6s ease";
        flash.style.opacity = "0";
        setTimeout(() => flash.remove(), 600);
      }, 4000);
    });
  })();

  /* ------------------ TIME AGO UPDATES ------------------ */
  (function timeAgoUpdater() {
    const timeAgo = (dateString) => {
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
    };

    const update = () => {
      document.querySelectorAll(".date").forEach((el) => {
        const time = el.dataset.time;
        if (time) el.textContent = timeAgo(time);
      });
    };
    update();
    setInterval(update, 60000);
  })();

  /* ------------------ VIDEO CONTAINERS ------------------ */
  (function videoContainers() {
    document.querySelectorAll('.video-container').forEach(container => {
      const video = container.querySelector('video');
      const overlay = container.querySelector('.play-overlay');
      if (!video || !overlay) return;
      overlay.addEventListener('click', () => { video.play(); });
      video.addEventListener('play', () => { container.classList.add('playing'); });
      video.addEventListener('pause', () => { container.classList.remove('playing'); });
    });
  })();

  

  /* ------------------ APPEARANCE TOGGLE (LIGHT / DARK MODE) ------------------ */
  const root = document.documentElement;
  const toggle = document.getElementById("appearance-toggle");
  const label = document.getElementById("mode-label");

  // Restore theme on load
  const savedTheme = localStorage.getItem("theme") || "light";
  root.setAttribute("data-theme", savedTheme);
  toggle.checked = savedTheme === "dark";
  label.textContent = savedTheme === "dark" ? "Dark Mode" : "Light Mode";

  // Toggle theme
  toggle.addEventListener("change", () => {
    const theme = toggle.checked ? "dark" : "light";
    root.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    label.textContent = theme === "dark" ? "Dark Mode" : "Light Mode";
  });
  

  

}); 
