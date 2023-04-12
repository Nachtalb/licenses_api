async function loadLicenseDetails(spdxId) {
  const response = await fetch(`/licenses/${spdxId}`)
  if (!response.ok) {
    console.error("Error fetching license details:", response.status)
    return
  }
  const license = await response.json()

  document.getElementById("api-license-link").href = `/licenses/${spdxId}`
  document.getElementById("api-license-raw-link").href = `/licenses/${spdxId}/raw`
  document.getElementById("license-spdx").textContent = license["spdx-id"]
  document.getElementById("license-title").textContent = license.title
  document.getElementById(
    "license-curl"
  ).textContent = `curl ${window.location.protocol}//${window.location.host}/licenses/${spdxId}/raw -o LICENSE`
  document.getElementById("license-description").innerHTML = license.description
  document.getElementById("license-how").innerHTML = license.how
  const nicknameElement = document.getElementById("license-nickname")
  const nicknameContainer = document.getElementById("license-nickname-container")
  if (license.nickname) {
    nicknameElement.textContent = license.nickname
    nicknameContainer.style.display = "block"
  } else {
    nicknameContainer.style.display = "none"
  }
  const noteElement = document.getElementById("license-note")
  const noteContainer = document.getElementById("license-note-container")
  if (license.note) {
    noteElement.innerHTML = license.note
    noteContainer.style.display = "block"
  } else {
    noteContainer.style.display = "none"
  }
  const usingElement = document.getElementById("license-using")
  const usingContainer = document.getElementById("license-using-container")
  if (Object.keys(license.using).length) {
    usingElement.innerHTML = Object.entries(license.using)
      .map(([name, url]) => `<li><a href="${url}">${name}</a></li>`)
      .join("")
    usingContainer.style.display = "block"
  } else {
    usingContainer.style.display = "none"
  }
  document.getElementById("license-permissions").innerHTML = license.permissions.map((p) => `<li>${p}</li>`).join("")
  document.getElementById("license-conditions").innerHTML = license.conditions.map((c) => `<li>${c}</li>`).join("")
  document.getElementById("license-limitations").innerHTML = license.limitations.map((l) => `<li>${l}</li>`).join("")
  document.getElementById("license-raw-content").textContent = license.content
}

document.getElementById("license-select").addEventListener("change", async function (event) {
  const spdxId = event.target.value
  if (!spdxId) {
    document.getElementById("license-details").style.display = "none"
    return
  }

  window.location.hash = spdxId
  await loadLicenseDetails(spdxId)
  document.getElementById("license-details").style.display = "block"
})

function loadLicenseFromUrlFragment() {
  const spdxId = window.location.hash.substring(1)
  if (spdxId) {
    const selectElement = document.getElementById("license-select")
    const optionElement = Array.from(selectElement.options).find((option) => option.value === spdxId)
    if (optionElement) {
      selectElement.value = spdxId
      loadLicenseDetails(spdxId)
      document.getElementById("license-details").style.display = "block"
    }
  }
}

window.addEventListener("DOMContentLoaded", loadLicenseFromUrlFragment)
window.addEventListener("hashchange", loadLicenseFromUrlFragment)

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(
    () => {
      console.log("Copied to clipboard successfully.")
      showToast("successToast")
    },
    () => {
      console.error("Failed to copy to clipboard.")
      showToast("errorToast")
    }
  )
}

document.querySelectorAll(".copy").forEach((element) => {
  element.addEventListener("click", () => {
    copyToClipboard(element.textContent)
  })
})

document.getElementById("copy-license-content").addEventListener("click", () => {
  const licenseContent = document.getElementById("license-raw-content").textContent
  copyToClipboard(licenseContent)
})

function showToast(toastId) {
  const toastElement = new bootstrap.Toast(document.getElementById(toastId))
  toastElement.show()
}
