(function () {
  "use strict";

  var INSTANCE_KEY = "__botcraftChatbotInstance";
  var scriptEl = document.currentScript || findScript();

  function findScript() {
    var scripts = Array.prototype.slice.call(document.getElementsByTagName("script"));
    return scripts.reverse().find(function (script) {
      return (
        (script.hasAttribute("data-workspace-id") || script.hasAttribute("workspaceId-attr")) &&
        script.src &&
        script.src.indexOf("chatbot.js") !== -1
      );
    });
  }

  function readAttr(script, names) {
    if (!script) return null;
    for (var i = 0; i < names.length; i += 1) {
      var value = script.getAttribute(names[i]);
      if (value) return value;
    }
    return null;
  }

  function toWsOrigin(origin) {
    var url = new URL(origin, window.location.href);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return url.origin;
  }

  function normalizeTheme(theme) {
    theme = theme || {};
    return {
      border_radius: theme.border_radius || theme.borderRadius,
      header_text: theme.header_text || theme.headerText,
      height: theme.height,
      input_placeholder: theme.input_placeholder || theme.inputPlaceholder,
      launcher: theme.launcher,
      position: theme.position,
      primary_color: theme.primary_color || theme.primaryColor,
      secondary_color: theme.secondary_color || theme.secondaryColor,
      show_header: theme.show_header !== undefined ? theme.show_header : theme.showHeader,
      text_color: theme.text_color || theme.textColor,
      theme: theme.theme,
      width: theme.width,
    };
  }

  function compactTheme(theme) {
    var compacted = {};
    Object.keys(theme).forEach(function (key) {
      if (theme[key] !== undefined && theme[key] !== null && theme[key] !== "") {
        compacted[key] = theme[key];
      }
    });
    return compacted;
  }

  function createSvgIcon(pathMarkup) {
    var wrapper = document.createElement("span");
    wrapper.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      pathMarkup +
      "</svg>";
    return wrapper.firstChild;
  }

  function BotCraftChatbot(config) {
    this.config = config;
    this.isOpen = false;
    this.messages = [];
    this.ws = null;
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.destroyed = false;
    this.defaultTheme = {
      border_radius: "8px",
      header_text: "Chat with me",
      height: "500px",
      input_placeholder: "Type your message here...",
      launcher: true,
      position: "bottom-right",
      primary_color: "#3B82F6",
      secondary_color: "#F3F4F6",
      show_header: true,
      text_color: "#000000",
      theme: "light",
      width: "350px",
    };
    this.theme = Object.assign({}, this.defaultTheme, compactTheme(normalizeTheme(config.theme)));
  }

  BotCraftChatbot.prototype.init = async function () {
    await this.fetchTheme();
    this.render();
    this.connectWebSocket();
  };

  BotCraftChatbot.prototype.destroy = function () {
    this.destroyed = true;
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
    }
    if (this.ws) {
      this.ws.close();
    }
    if (this.container && this.container.parentNode) {
      this.container.parentNode.removeChild(this.container);
    }
    if (this.launcher && this.launcher.parentNode) {
      this.launcher.parentNode.removeChild(this.launcher);
    }
  };

  BotCraftChatbot.prototype.fetchTheme = async function () {
    if (!this.config.workspaceId) return;

    try {
      var response = await fetch(
        this.config.apiOrigin.replace(/\/$/, "") +
          "/api/v1/theme?workspace_id=" +
          encodeURIComponent(this.config.workspaceId)
      );
      if (!response.ok) throw new Error("Theme request failed");
      var data = await response.json();
      this.theme = Object.assign(
        {},
        this.defaultTheme,
        compactTheme(normalizeTheme(data)),
        compactTheme(normalizeTheme(this.config.theme))
      );
    } catch (error) {
      console.warn("[BotCraft] Using default theme:", error);
    }
  };

  BotCraftChatbot.prototype.buildWebSocketUrl = function () {
    if (this.config.wsEndpoint) {
      return this.withWorkspaceParam(this.config.wsEndpoint);
    }

    return this.withWorkspaceParam(
      this.config.wsOrigin.replace(/\/$/, "") + "/api/v1/playground/chat"
    );
  };

  BotCraftChatbot.prototype.withWorkspaceParam = function (url) {
    var parsed = new URL(url, window.location.href);
    parsed.searchParams.set("workspace_id", this.config.workspaceId);
    return parsed.toString();
  };

  BotCraftChatbot.prototype.connectWebSocket = function () {
    if (this.destroyed || !this.config.workspaceId) return;

    this.ws = new WebSocket(this.buildWebSocketUrl());

    this.ws.onopen = function () {
      this.reconnectAttempts = 0;
      if (!this.messages.length) {
        this.addMessage({
          text: "Hello! How can I help you today?",
          isUser: false,
          timestamp: new Date(),
        });
      }
    }.bind(this);

    this.ws.onmessage = function (event) {
      this.addMessage({
        text: event.data,
        isUser: false,
        timestamp: new Date(),
      });
    }.bind(this);

    this.ws.onerror = function () {
      if (!this.messages.some(function (message) { return message.kind === "connection-error"; })) {
        this.addMessage({
          text: "I am having trouble connecting. Please try again in a moment.",
          isUser: false,
          timestamp: new Date(),
          kind: "connection-error",
        });
      }
    }.bind(this);

    this.ws.onclose = function () {
      if (this.destroyed) return;
      var delay = Math.min(30000, 1000 * Math.pow(2, this.reconnectAttempts));
      this.reconnectAttempts += 1;
      this.reconnectTimer = window.setTimeout(this.connectWebSocket.bind(this), delay);
    }.bind(this);
  };

  BotCraftChatbot.prototype.injectStyles = function () {
    if (document.getElementById("botcraft-widget-styles")) return;

    var style = document.createElement("style");
    style.id = "botcraft-widget-styles";
    style.textContent = [
      ".botcraft-widget,.botcraft-widget *{box-sizing:border-box;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}",
      ".botcraft-widget{position:fixed;z-index:2147483647;display:none;flex-direction:column;overflow:hidden;border:1px solid rgba(15,23,42,.12);box-shadow:0 24px 80px rgba(15,23,42,.22);}",
      ".botcraft-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-bottom:1px solid rgba(148,163,184,.35);}",
      ".botcraft-title{margin:0;font-size:15px;line-height:20px;font-weight:700;letter-spacing:0;color:inherit;}",
      ".botcraft-close,.botcraft-send,.botcraft-launcher{appearance:none;border:0;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;}",
      ".botcraft-close{width:30px;height:30px;border-radius:999px;background:transparent;color:inherit;}",
      ".botcraft-close:hover{background:rgba(148,163,184,.18);}",
      ".botcraft-messages{flex:1;min-height:0;overflow-y:auto;padding:16px;}",
      ".botcraft-message-row{display:flex;margin:0 0 12px;}",
      ".botcraft-message-row.user{justify-content:flex-end;}",
      ".botcraft-bubble{max-width:82%;border-radius:14px;padding:10px 12px;overflow-wrap:anywhere;}",
      ".botcraft-bubble p{margin:0;font-size:14px;line-height:20px;letter-spacing:0;}",
      ".botcraft-time{display:block;margin-top:4px;font-size:11px;line-height:14px;opacity:.62;}",
      ".botcraft-form{display:flex;gap:8px;padding:12px;border-top:1px solid rgba(148,163,184,.35);}",
      ".botcraft-input{min-width:0;flex:1;border:1px solid rgba(148,163,184,.55);border-radius:8px;padding:10px 11px;font-size:14px;line-height:20px;outline:none;background:#fff;color:#0f172a;}",
      ".botcraft-input:focus{border-color:rgba(59,130,246,.8);box-shadow:0 0 0 3px rgba(59,130,246,.14);}",
      ".botcraft-send{width:42px;height:42px;border-radius:8px;color:#fff;}",
      ".botcraft-launcher{position:fixed;width:56px;height:56px;border-radius:999px;color:#fff;z-index:2147483646;box-shadow:0 14px 40px rgba(15,23,42,.28);transition:transform .18s ease;}",
      ".botcraft-launcher:hover{transform:translateY(-1px) scale(1.03);}",
      "@media (max-width:480px){.botcraft-widget{width:calc(100vw - 32px)!important;height:min(620px,calc(100vh - 112px))!important;}.botcraft-bubble{max-width:90%;}}",
    ].join("");
    document.head.appendChild(style);
  };

  BotCraftChatbot.prototype.applyPosition = function (element, offset) {
    var position = this.theme.position || "bottom-right";
    element.style.top = "";
    element.style.right = "";
    element.style.bottom = "";
    element.style.left = "";

    if (position.indexOf("top") === 0) {
      element.style.top = offset;
    } else {
      element.style.bottom = offset;
    }

    if (position.indexOf("left") !== -1) {
      element.style.left = "20px";
    } else {
      element.style.right = "20px";
    }
  };

  BotCraftChatbot.prototype.render = function () {
    this.injectStyles();

    this.container = document.createElement("section");
    this.container.className = "botcraft-widget";
    this.container.setAttribute("aria-live", "polite");
    this.container.style.width = this.theme.width;
    this.container.style.height = this.theme.height;
    this.container.style.borderRadius = this.theme.border_radius;
    this.container.style.background = this.theme.theme === "dark" ? "#111827" : "#ffffff";
    this.container.style.color = this.theme.theme === "dark" ? "#ffffff" : this.theme.text_color;
    this.applyPosition(this.container, "86px");

    if (this.theme.show_header) {
      var header = document.createElement("header");
      header.className = "botcraft-header";

      var title = document.createElement("h2");
      title.className = "botcraft-title";
      title.textContent = this.theme.header_text;

      var close = document.createElement("button");
      close.className = "botcraft-close";
      close.type = "button";
      close.setAttribute("aria-label", "Close chat");
      close.textContent = "x";
      close.addEventListener("click", this.toggleChatbot.bind(this, false));

      header.appendChild(title);
      header.appendChild(close);
      this.container.appendChild(header);
    }

    this.messageArea = document.createElement("div");
    this.messageArea.className = "botcraft-messages";
    this.container.appendChild(this.messageArea);

    var form = document.createElement("form");
    form.className = "botcraft-form";
    form.addEventListener("submit", this.handleSubmit.bind(this));

    this.input = document.createElement("input");
    this.input.className = "botcraft-input";
    this.input.type = "text";
    this.input.placeholder = this.theme.input_placeholder;
    this.input.autocomplete = "off";

    var submit = document.createElement("button");
    submit.className = "botcraft-send";
    submit.type = "submit";
    submit.style.background = this.theme.primary_color;
    submit.setAttribute("aria-label", "Send message");
    submit.appendChild(
      createSvgIcon('<path d="M22 2 11 13"></path><path d="m22 2-7 20-4-9-9-4 20-7Z"></path>')
    );

    form.appendChild(this.input);
    form.appendChild(submit);
    this.container.appendChild(form);
    document.body.appendChild(this.container);

    if (this.theme.launcher) {
      this.launcher = document.createElement("button");
      this.launcher.className = "botcraft-launcher";
      this.launcher.type = "button";
      this.launcher.style.background = this.theme.primary_color;
      this.launcher.setAttribute("aria-label", "Open chat");
      this.launcher.appendChild(
        createSvgIcon('<path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"></path><path d="M8 9h8"></path><path d="M8 13h6"></path>')
      );
      this.applyPosition(this.launcher, "20px");
      this.launcher.addEventListener("click", this.toggleChatbot.bind(this, true));
      document.body.appendChild(this.launcher);
    } else {
      this.toggleChatbot(true);
    }
  };

  BotCraftChatbot.prototype.toggleChatbot = function (show) {
    this.isOpen = typeof show === "boolean" ? show : !this.isOpen;
    this.container.style.display = this.isOpen ? "flex" : "none";
    if (this.launcher) {
      this.launcher.style.display = this.isOpen ? "none" : "inline-flex";
    }
    if (this.isOpen && this.input) {
      this.input.focus();
      this.messageArea.scrollTop = this.messageArea.scrollHeight;
    }
  };

  BotCraftChatbot.prototype.handleSubmit = function (event) {
    event.preventDefault();
    var message = this.input.value.trim();
    if (!message) return;

    this.addMessage({ text: message, isUser: true, timestamp: new Date() });
    this.input.value = "";

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message);
      return;
    }

    this.addMessage({
      text: "I am reconnecting. Please send that again in a moment.",
      isUser: false,
      timestamp: new Date(),
    });
  };

  BotCraftChatbot.prototype.addMessage = function (message) {
    this.messages.push(message);
    if (!this.messageArea) return;

    var row = document.createElement("div");
    row.className = "botcraft-message-row" + (message.isUser ? " user" : "");

    var bubble = document.createElement("div");
    bubble.className = "botcraft-bubble";
    bubble.style.background = message.isUser
      ? this.theme.primary_color
      : this.theme.theme === "dark"
        ? "#1f2937"
        : this.theme.secondary_color;
    bubble.style.color = message.isUser
      ? "#ffffff"
      : this.theme.theme === "dark"
        ? "#ffffff"
        : this.theme.text_color;

    var text = document.createElement("p");
    text.textContent = message.text;

    var time = document.createElement("span");
    time.className = "botcraft-time";
    time.textContent = message.timestamp.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    bubble.appendChild(text);
    bubble.appendChild(time);
    row.appendChild(bubble);
    this.messageArea.appendChild(row);
    this.messageArea.scrollTop = this.messageArea.scrollHeight;
  };

  function getConfig(overrideConfig) {
    var scriptUrl = new URL(scriptEl && scriptEl.src ? scriptEl.src : window.location.href);
    var apiOrigin =
      overrideConfig.apiOrigin ||
      readAttr(scriptEl, ["data-api-origin"]) ||
      scriptUrl.origin;
    var wsOrigin =
      overrideConfig.wsOrigin ||
      readAttr(scriptEl, ["data-ws-origin"]) ||
      toWsOrigin(apiOrigin);

    return {
      apiOrigin: apiOrigin,
      wsOrigin: wsOrigin,
      wsEndpoint:
        overrideConfig.wsEndpoint || readAttr(scriptEl, ["data-ws-endpoint"]),
      workspaceId:
        overrideConfig.workspaceId ||
        readAttr(scriptEl, ["data-workspace-id", "workspaceId-attr", "workspaceid-attr"]),
      theme: overrideConfig.theme || {},
    };
  }

  window.initChatbot = function (overrideConfig) {
    var config = getConfig(overrideConfig || {});
    if (!config.workspaceId) {
      console.error("[BotCraft] Missing data-workspace-id on chatbot script tag.");
      return;
    }

    if (window[INSTANCE_KEY]) {
      window[INSTANCE_KEY].destroy();
    }

    var chatbot = new BotCraftChatbot(config);
    window[INSTANCE_KEY] = chatbot;
    chatbot.init();
  };

  function boot() {
    if (scriptEl && scriptEl.dataset.botcraftInitialized === "true") return;
    if (scriptEl) scriptEl.dataset.botcraftInitialized = "true";
    window.initChatbot({});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
