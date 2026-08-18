// Tests unitarios para la función `convert` (y sus helpers `toUSD`/`fromUSD`)
// del conversor de monedas.
//
// La lógica de conversión vive embebida como <script> inline dentro de
// conversor-takenos.html (generado por build.py) dentro de una IIFE que no
// exporta nada. Para testear el código *real* tal como se shippea (sin
// modificarlo ni reimplementarlo a mano), este archivo extrae el bloque de
// RATES + toUSD/fromUSD/convert directamente del HTML y lo ejecuta en un
// contexto vm de Node.
//
// Correr con: node --test conversor/convert.test.js

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test, describe, beforeEach } = require("node:test");
const assert = require("node:assert/strict");

const HTML_PATH = path.join(__dirname, "conversor-takenos.html");
const html = fs.readFileSync(HTML_PATH, "utf8");

function sliceBetween(text, startMarker, endMarker, label) {
  const start = text.indexOf(startMarker);
  if (start === -1) {
    throw new Error(`No se encontró el marcador de inicio "${startMarker}" (${label}). ¿Cambió conversor-takenos.html?`);
  }
  const end = text.indexOf(endMarker, start);
  if (end === -1) {
    throw new Error(`No se encontró el marcador de fin "${endMarker}" (${label}). ¿Cambió conversor-takenos.html?`);
  }
  return text.slice(start, end);
}

const ratesLiteral = sliceBetween(html, "  var RATES = {", "\n  RATES.USD", "RATES");
const ratesUsdLine = sliceBetween(html, "  RATES.USD = {", "\n  var FLAGS", "RATES.USD");
const functionsBlock = sliceBetween(
  html,
  "  function toUSD(amount, cur) {",
  "\n  function fmt(value, cur) {",
  "toUSD/fromUSD/convert"
);

const sandboxSource = `
${ratesLiteral}
${ratesUsdLine}
${functionsBlock}
module.exports = { RATES, toUSD, fromUSD, convert };
`;

const sandboxModule = { exports: {} };
vm.runInNewContext(sandboxSource, { module: sandboxModule });

const { RATES, toUSD, fromUSD, convert } = sandboxModule.exports;
const PRISTINE_RATES = JSON.parse(JSON.stringify(RATES));

function resetRates() {
  for (const key of Object.keys(RATES)) delete RATES[key];
  Object.assign(RATES, JSON.parse(JSON.stringify(PRISTINE_RATES)));
}

beforeEach(resetRates);

describe("convert() — sanity sobre las tasas extraídas", () => {
  test("RATES trae USD y al menos ARS/BOB con buy y sell numéricos", () => {
    assert.equal(RATES.USD.buy, 1);
    assert.equal(RATES.USD.sell, 1);
    assert.equal(typeof RATES.ARS.buy, "number");
    assert.equal(typeof RATES.ARS.sell, "number");
    assert.equal(typeof RATES.BOB.buy, "number");
    assert.equal(typeof RATES.BOB.sell, "number");
  });
});

describe("convert() — distintas monedas", () => {
  test("USD -> ARS usa el sell de ARS", () => {
    const result = convert(100, "USD", "ARS");
    assert.equal(result, 100 * RATES.ARS.sell);
  });

  test("ARS -> USD usa el buy de ARS", () => {
    const result = convert(1000, "ARS", "USD");
    assert.equal(result, 1000 / RATES.ARS.buy);
  });

  test("moneda -> moneda (ninguna USD) encadena buy del origen y sell del destino", () => {
    const result = convert(1000, "ARS", "BOB");
    const expected = (1000 / RATES.ARS.buy) * RATES.BOB.sell;
    assert.ok(Math.abs(result - expected) < 1e-9);
  });

  test("es asimétrico: ida y vuelta no devuelve el monto original (spread buy/sell)", () => {
    const there = convert(1000, "USD", "ARS");
    const back = convert(there, "ARS", "USD");
    assert.notEqual(back, 1000);
    // El "back" debe ser menor o igual al original porque sell <= buy (spread de la casa).
    assert.ok(back <= 1000);
  });

  test("from === to devuelve el monto sin tocar RATES, incluso para una moneda inexistente", () => {
    // Caso patológico real de la implementación actual: el shortcut de
    // igualdad se evalúa antes de mirar RATES, así que un código inválido
    // no explota si from y to son el mismo string.
    assert.equal(convert(123.45, "USD", "USD"), 123.45);
    assert.equal(convert(50, "ZZZ", "ZZZ"), 50);
  });
});

describe("convert() — montos en cero", () => {
  test("0 en cualquier par de monedas válidas da 0", () => {
    assert.equal(convert(0, "USD", "ARS"), 0);
    assert.equal(convert(0, "ARS", "USD"), 0);
    assert.equal(convert(0, "ARS", "BOB"), 0);
  });

  test("0 NO evita el error si la moneda de destino no existe (falla antes de multiplicar)", () => {
    // fromUSD hace `amountUsd * RATES[cur].sell`: el acceso a `.sell` sobre
    // `undefined` explota aunque amountUsd sea 0, porque la lectura de la
    // propiedad ocurre antes de la multiplicación.
    assert.throws(() => convert(0, "USD", "NOPE"), { name: "TypeError" });
  });
});

describe("convert() — montos negativos", () => {
  test("un monto negativo se convierte sin ninguna validación (no se rechaza)", () => {
    const result = convert(-100, "USD", "ARS");
    assert.equal(result, -100 * RATES.ARS.sell);
    assert.ok(result < 0);
  });

  test("negativo -> negativo -> negativo se mantiene consistente entre monedas no-USD", () => {
    const result = convert(-500, "ARS", "BOB");
    const expected = (-500 / RATES.ARS.buy) * RATES.BOB.sell;
    assert.ok(Math.abs(result - expected) < 1e-9);
    assert.ok(result < 0);
  });
});

describe("convert() — tasas de cambio inválidas o que fallan", () => {
  test("moneda de origen inexistente lanza TypeError (lee .buy de undefined)", () => {
    assert.throws(() => convert(100, "NOPE", "USD"), { name: "TypeError" });
  });

  test("moneda de destino inexistente lanza TypeError (lee .sell de undefined)", () => {
    assert.throws(() => convert(100, "USD", "NOPE"), { name: "TypeError" });
  });

  test("código de moneda con capitalización distinta se trata como inexistente", () => {
    // RATES usa claves en mayúsculas; "usd"/"ars" en minúscula no matchean
    // ni el shortcut `cur === "USD"` ni las claves de RATES.
    assert.throws(() => convert(100, "usd", "ars"), { name: "TypeError" });
  });

  test("tasa buy en 0 produce división por cero -> Infinity, no un error", () => {
    RATES.ARS.buy = 0;
    const result = convert(100, "ARS", "USD");
    assert.equal(result, Infinity);
  });

  test("tasa sell en 0 produce 0 como resultado de la conversión", () => {
    RATES.ARS.sell = 0;
    const result = convert(100, "USD", "ARS");
    assert.equal(result, 0);
  });

  test("tasa negativa se aplica igual, sin ninguna validación de rango", () => {
    RATES.ARS.sell = -1555.12;
    const result = convert(100, "USD", "ARS");
    assert.equal(result, -155512);
  });

  test("tasa NaN contamina el resultado con NaN en lugar de fallar", () => {
    RATES.ARS.buy = NaN;
    const result = convert(100, "ARS", "USD");
    assert.ok(Number.isNaN(result));
  });

  test("entrada de moneda corrupta (null) lanza TypeError al leer la tasa", () => {
    RATES.ARS = null;
    assert.throws(() => convert(100, "USD", "ARS"), { name: "TypeError" });
  });

  test("toUSD y fromUSD replican los mismos fallos que convert() para moneda inexistente", () => {
    assert.throws(() => toUSD(100, "NOPE"), { name: "TypeError" });
    assert.throws(() => fromUSD(100, "NOPE"), { name: "TypeError" });
  });
});
