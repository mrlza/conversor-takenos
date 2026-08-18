/**
 * Web App de Apps Script que expone la cotización USDT/Takenos de la API de
 * Dolarito como un endpoint JSON público con CORS abierto, para que un sitio
 * estático (GitHub Pages, en este caso) pueda leerla en el navegador sin
 * chocar con el CORS restrictivo de api.dolarito.ar (solo permite
 * www.dolarito.ar como origin).
 *
 * El fetch a Dolarito corre server-side en la infraestructura de Google, así
 * que no aplica ninguna restricción de CORS ahí adentro.
 *
 * DEPLOY:
 *   1. Extensiones > Apps Script en tu Google Sheet (o un proyecto standalone
 *      en script.google.com si no necesitás guardar nada en un Sheet).
 *   2. Pegá este archivo como un .gs nuevo.
 *   3. Implementar > Nueva implementación > tipo "Aplicación web".
 *        - Ejecutar como: Yo
 *        - Quién tiene acceso: Cualquier usuario
 *   4. Copiá la URL que termina en /exec — esa es LIVE_RATE_URL en build.py.
 *   5. Pegala en build.py (LIVE_RATE_URL = "...") y corré `python3 build.py`
 *      para regenerar conversor-takenos.html con el fetch en vivo activado.
 *
 * Cada redeploy del código (no de la config) genera una URL /exec nueva, así
 * que después de editar este script hay que crear una implementación nueva y
 * actualizar build.py con la URL final.
 */
function doGet(e) {
  var url = "https://api.dolarito.ar/api/frontend/quotations/usdt";
  var options = {
    method: "get",
    headers: {
      "auth-client": "3d3456e64d4307a9b0564b3c0c03a5a9",
      "Content-Type": "application/json"
    },
    muteHttpExceptions: true
  };

  var payload;
  try {
    var response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() !== 200) {
      payload = { error: "upstream_error", status: response.getResponseCode() };
    } else {
      var json = JSON.parse(response.getContentText());
      var takenos = json.takenos;
      if (!takenos || typeof takenos !== "object") {
        payload = { error: "no_data" };
      } else {
        payload = {
          name: takenos.name || "Takenos",
          buy: Number(takenos.buy) || 0,
          sell: Number(takenos.sell) || 0,
          spread: Number(takenos.spread) || 0,
          sourceTimestamp: takenos.timestamp || null,
          fetchedAt: new Date().toISOString()
        };
      }
    }
  } catch (err) {
    payload = { error: "script_error", message: err.toString() };
  }

  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
