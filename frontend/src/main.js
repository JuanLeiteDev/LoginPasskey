const API_BASE_URL = (
  import.meta.env?.VITE_API_BASE_URL || window.__API_BASE_URL__ || "/api"
).replace(/\/$/, "");

const endpoints = {
  registerOptions: "/ChaveDeAcesso/Registrar/Opcoes",
  registerVerify: "/ChaveDeAcesso/Registrar/Verificar",
  authOptions: "/ChaveDeAcesso/Autenticar/Opcoes",
  authVerify: "/ChaveDeAcesso/Autenticar/Verificar",
};

const loginTab = document.querySelector("#login-tab");
const registerTab = document.querySelector("#register-tab");
const loginPanel = document.querySelector("#login-panel");
const registerPanel = document.querySelector("#register-panel");
const loginButton = document.querySelector("#login-button");
const registerButton = document.querySelector("#register-button");
const toast = document.querySelector("#toast");
let toastTimer;
let activeRpId;

function selectTab(tab) {
  const isLogin = tab === "login";
  loginTab.classList.toggle("active", isLogin);
  registerTab.classList.toggle("active", !isLogin);
  loginPanel.classList.toggle("active", isLogin);
  registerPanel.classList.toggle("active", !isLogin);
  loginTab.setAttribute("aria-selected", String(isLogin));
  registerTab.setAttribute("aria-selected", String(!isLogin));
}

loginTab.addEventListener("click", () => selectTab("login"));
registerTab.addEventListener("click", () => selectTab("register"));

function setLoading(button, loading) {
  button.disabled = loading;
  button.classList.toggle("loading", loading);
  button.setAttribute("aria-busy", String(loading));
}

function showToast(type, title, message) {
  window.clearTimeout(toastTimer);
  toast.className = `toast show ${type}`;
  document.querySelector("#toast-title").textContent = title;
  document.querySelector("#toast-message").textContent = message;
  document.querySelector(".toast-icon").textContent = type === "success" ? "✓" : type === "info" ? "i" : "!";
  toastTimer = window.setTimeout(() => toast.classList.remove("show"), 6500);
}

document.querySelector("#toast-close").addEventListener("click", () => toast.classList.remove("show"));

function bufferToBase64URL(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let index = 0; index < bytes.byteLength; index += 1) {
    binary += String.fromCharCode(bytes[index]);
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function base64URLToBuffer(value) {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function normalizeOptions(payload) {
  let normalized = payload;
  // A rota atual devolve options_to_json(), portanto pode existir uma segunda
  // camada JSON. Este tratamento também funciona quando o backend a remover.
  while (typeof normalized === "string") {
    normalized = JSON.parse(normalized);
  }
  return normalized?.publicKey || normalized;
}

async function apiRequest(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
  } catch {
    throw new Error("Não foi possível ligar ao servidor. Confirme se o backend está em execução.");
  }

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const details = Array.isArray(data?.detail)
      ? data.detail.map((item) => item.msg).join(" · ")
      : data?.detail;
    throw new Error(details || "O servidor não conseguiu concluir o pedido.");
  }

  return data;
}

function creationOptionsFromJSON(options) {
  const publicKey = normalizeOptions(options);
  if (!publicKey?.challenge || !publicKey?.user?.id) {
    throw new Error("O servidor devolveu opções de registo incompletas.");
  }

  activeRpId = publicKey.rp?.id;

  return {
    ...publicKey,
    challenge: base64URLToBuffer(publicKey.challenge),
    user: { ...publicKey.user, id: base64URLToBuffer(publicKey.user.id) },
    excludeCredentials: (publicKey.excludeCredentials || []).map((credential) => ({
      ...credential,
      id: base64URLToBuffer(credential.id),
    })),
  };
}

function requestOptionsFromJSON(options) {
  const publicKey = normalizeOptions(options);
  if (!publicKey?.challenge) {
    const error = new Error("A autenticação por passkey ainda está a ser preparada no servidor.");
    error.code = "BACKEND_PENDING";
    throw error;
  }

  return {
    ...publicKey,
    challenge: base64URLToBuffer(publicKey.challenge),
    allowCredentials: (publicKey.allowCredentials || []).map((credential) => ({
      ...credential,
      id: base64URLToBuffer(credential.id),
    })),
  };
}

function serializeRegistration(credential) {
  const response = credential.response;
  return {
    id: credential.id,
    rawId: bufferToBase64URL(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64URL(response.clientDataJSON),
      attestationObject: bufferToBase64URL(response.attestationObject),
      transports: response.getTransports?.() || [],
    },
    authenticatorAttachment: credential.authenticatorAttachment,
    clientExtensionResults: credential.getClientExtensionResults(),
  };
}

function serializeAuthentication(credential) {
  const response = credential.response;
  return {
    id: credential.id,
    rawId: bufferToBase64URL(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64URL(response.clientDataJSON),
      authenticatorData: bufferToBase64URL(response.authenticatorData),
      signature: bufferToBase64URL(response.signature),
      userHandle: response.userHandle ? bufferToBase64URL(response.userHandle) : null,
    },
    authenticatorAttachment: credential.authenticatorAttachment,
    clientExtensionResults: credential.getClientExtensionResults(),
  };
}

function assertPasskeySupport() {
  if (!window.PublicKeyCredential || !navigator.credentials) {
    throw new Error("Este navegador não suporta passkeys. Experimente uma versão recente do Chrome, Edge, Firefox ou Safari.");
  }
  if (!window.isSecureContext) {
    throw new Error("As passkeys exigem HTTPS. Em desenvolvimento, abra o frontend através de localhost.");
  }
}

function friendlyCredentialError(error) {
  if (error.name === "NotAllowedError") {
    return "A operação foi cancelada ou excedeu o tempo disponível. Pode tentar novamente.";
  }
  if (error.name === "InvalidStateError") {
    return "Este dispositivo já tem uma passkey associada a esta conta.";
  }
  if (error.name === "SecurityError") {
    const rpDetails = activeRpId ? ` O servidor definiu o RP ID como “${activeRpId}”.` : "";
    return `A página está aberta em “${window.location.origin}”.${rpDetails} Em desenvolvimento, abra exatamente http://localhost:8000.`;
  }
  return error.message || "Não foi possível concluir a operação com a passkey.";
}

function validateRegistrationForm() {
  const name = document.querySelector("#name");
  const email = document.querySelector("#email");
  const nameError = document.querySelector("#name-error");
  const emailError = document.querySelector("#email-error");
  let valid = true;

  nameError.textContent = "";
  emailError.textContent = "";
  name.closest(".field").classList.remove("invalid");
  email.closest(".field").classList.remove("invalid");

  if (name.value.trim().length < 2 || /\d/.test(name.value)) {
    nameError.textContent = "Indique um nome válido, sem números.";
    name.closest(".field").classList.add("invalid");
    valid = false;
  }
  if (!email.validity.valid) {
    emailError.textContent = "Indique um endereço de email válido.";
    email.closest(".field").classList.add("invalid");
    valid = false;
  }

  return valid;
}

registerPanel.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!validateRegistrationForm()) return;

  setLoading(registerButton, true);
  try {
    assertPasskeySupport();
    const options = await apiRequest(endpoints.registerOptions, {
      method: "POST",
      body: JSON.stringify({
        name: document.querySelector("#name").value.trim(),
        email: document.querySelector("#email").value.trim().toLowerCase(),
      }),
    });
    const credential = await navigator.credentials.create({
      publicKey: creationOptionsFromJSON(options),
    });
    if (!credential) throw new Error("O navegador não devolveu uma credencial.");

    await apiRequest(endpoints.registerVerify, {
      method: "POST",
      body: JSON.stringify(serializeRegistration(credential)),
    });
    registerPanel.reset();
    showToast("success", "Passkey criada", "A sua conta está pronta. Já pode entrar sem palavra-passe.");
    selectTab("login");
  } catch (error) {
    showToast("error", "Não foi possível criar a conta", friendlyCredentialError(error));
  } finally {
    setLoading(registerButton, false);
  }
});

loginButton.addEventListener("click", async () => {
  setLoading(loginButton, true);
  try {
    assertPasskeySupport();
    const options = await apiRequest(endpoints.authOptions, {
      method: "POST",
      body: JSON.stringify({}),
    });
    const credential = await navigator.credentials.get({
      publicKey: requestOptionsFromJSON(options),
    });
    if (!credential) throw new Error("O navegador não devolveu uma credencial.");

    await apiRequest(endpoints.authVerify, {
      method: "POST",
      body: JSON.stringify(serializeAuthentication(credential)),
    });
    showToast("success", "Sessão iniciada", "A sua identidade foi confirmada com segurança.");
  } catch (error) {
    const pending = error.code === "BACKEND_PENDING";
    showToast(
      pending ? "info" : "error",
      pending ? "Funcionalidade em preparação" : "Não foi possível entrar",
      friendlyCredentialError(error),
    );
  } finally {
    setLoading(loginButton, false);
  }
});

document.querySelectorAll("input").forEach((input) => {
  input.addEventListener("input", () => input.closest(".field")?.classList.remove("invalid"));
});

if (!window.PublicKeyCredential) {
  document.querySelector("#security-pill").innerHTML = '<span class="pulse warning"></span> Passkeys indisponíveis';
}
