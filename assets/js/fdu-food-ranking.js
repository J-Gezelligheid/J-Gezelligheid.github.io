(function () {
  const seedEl = document.getElementById("food-ranking-seed");
  if (!seedEl) return;

  const LOCAL_STORAGE_KEY = "fdu_food_ranking_state_v1";
  const REQUIRED_AREAS = [
    { id: "guoquan-road", name: "国权路" },
    { id: "sanhao-bay", name: "三号湾" },
    { id: "wujiaochang", name: "五角场" },
  ];

  const ui = {
    mode: document.getElementById("food-board-store-mode"),
    rankingBody: document.getElementById("food-ranking-table-body"),
    areaGrid: document.getElementById("food-area-grid"),
    ratingForm: document.getElementById("food-rating-form"),
    ratingShop: document.getElementById("food-rating-shop"),
    ratingScore: document.getElementById("food-rating-score"),
    ratingUser: document.getElementById("food-rating-user"),
    ratingSubmit: document.getElementById("food-rating-submit"),
    ratingMessage: document.getElementById("food-rating-message"),
    addShopForm: document.getElementById("food-add-shop-form"),
    addShopArea: document.getElementById("food-add-shop-area"),
    addShopName: document.getElementById("food-add-shop-name"),
    addShopOwner: document.getElementById("food-add-shop-owner"),
    addShopSubmit: document.getElementById("food-add-shop-submit"),
    addShopMessage: document.getElementById("food-add-shop-message"),
  };

  let seed = {};
  try {
    seed = JSON.parse(seedEl.textContent || "{}");
  } catch (_) {
    seed = {};
  }

  const areas = normalizeAreas(seed.areas);
  const areaMap = {};
  areas.forEach(function (area) {
    areaMap[area.id] = area;
  });

  const seedShops = buildSeedShops(areas);
  let storeMode = "local";
  let storeModeMessage = "本地模式：评分仅保存在当前浏览器。";
  let remoteConfig = null;

  const state = {
    shops: seedShops.slice(),
    ratings: [],
  };

  init();

  function init() {
    bindEvents();
    initSmoothAnchor();
    hydrateAreaSelect();
    loadState().then(function () {
      renderAll();
    });
  }

  async function loadState() {
    const firebase = seed && seed.firebase ? seed.firebase : {};
    const isRemoteReady =
      firebase.enabled === true &&
      typeof firebase.database_url === "string" &&
      firebase.database_url.trim();

    let persisted = { shops: [], ratings: [] };

    if (isRemoteReady) {
      remoteConfig = {
        databaseUrl: firebase.database_url.trim().replace(/\/+$/, ""),
        dataRoot:
          typeof firebase.data_root === "string" && firebase.data_root.trim()
            ? firebase.data_root.trim().replace(/^\/+|\/+$/g, "")
            : "fdu_food_ranking",
      };
      storeMode = "remote";
      storeModeMessage = "共享模式：所有访客评分会汇总计算均值。";

      try {
        persisted = await readRemoteState();
      } catch (_) {
        storeMode = "local";
        remoteConfig = null;
        storeModeMessage =
          "共享模式连接失败，已回退到本地模式（仅当前浏览器可见）。";
        persisted = readLocalState();
      }
    } else {
      persisted = readLocalState();
    }

    state.shops = mergeShops(seedShops.concat(persisted.shops || []));
    const validShopIds = new Set(
      state.shops.map(function (shop) {
        return shop.id;
      })
    );
    state.ratings = normalizeRatings(persisted.ratings || []).filter(function (
      rating
    ) {
      return validShopIds.has(rating.shop_id);
    });

    saveLocalState();
  }

  async function readRemoteState() {
    const response = await fetch(remoteUrl(""), { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Failed to fetch shared rating state.");
    }

    const payload = await response.json();
    if (!payload || typeof payload !== "object") {
      return { shops: [], ratings: [] };
    }

    return {
      shops: normalizeRemoteCollection(payload.shops, true),
      ratings: normalizeRemoteCollection(payload.ratings, true),
    };
  }

  async function writeRemoteItem(collection, item) {
    if (!remoteConfig) return;
    const response = await fetch(
      remoteUrl(collection + "/" + encodeURIComponent(item.id)),
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to write shared rating state.");
    }
  }

  function readLocalState() {
    try {
      const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (!raw) return { shops: [], ratings: [] };
      const parsed = JSON.parse(raw);
      return {
        shops: Array.isArray(parsed.shops) ? parsed.shops : [],
        ratings: Array.isArray(parsed.ratings) ? parsed.ratings : [],
      };
    } catch (_) {
      return { shops: [], ratings: [] };
    }
  }

  function saveLocalState() {
    try {
      localStorage.setItem(
        LOCAL_STORAGE_KEY,
        JSON.stringify({
          shops: state.shops,
          ratings: state.ratings,
        })
      );
    } catch (_) {
      // Ignore storage errors to keep UI responsive.
    }
  }

  function remoteUrl(path) {
    const base = remoteConfig.databaseUrl;
    const root = remoteConfig.dataRoot;
    const suffix = path ? "/" + path : "";
    return base + "/" + root + suffix + ".json";
  }

  function normalizeAreas(rawAreas) {
    const normalized = [];
    const rawById = {};

    if (Array.isArray(rawAreas)) {
      rawAreas.forEach(function (entry) {
        if (!entry || typeof entry !== "object") return;
        const id = toCleanId(entry.id);
        if (!id) return;
        rawById[id] = entry;
      });
    }

    REQUIRED_AREAS.forEach(function (requiredArea) {
      const incoming = rawById[requiredArea.id] || {};
      normalized.push({
        id: requiredArea.id,
        name:
          typeof incoming.name === "string" && incoming.name.trim()
            ? incoming.name.trim()
            : requiredArea.name,
        shops: Array.isArray(incoming.shops) ? incoming.shops : [],
      });
    });

    return normalized;
  }

  function buildSeedShops(areasList) {
    const shops = [];
    areasList.forEach(function (area) {
      area.shops.forEach(function (shop) {
        const normalized = normalizeShop(shop, area.id);
        if (normalized) shops.push(normalized);
      });
    });
    return mergeShops(shops);
  }

  function normalizeRemoteCollection(payload, includeIdFromKey) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== "object") return [];
    return Object.keys(payload)
      .map(function (key) {
        const item = payload[key];
        if (!item || typeof item !== "object") return null;
        if (includeIdFromKey && !item.id) {
          item.id = key;
        }
        return item;
      })
      .filter(Boolean);
  }

  function mergeShops(shops) {
    const seen = {};
    const merged = [];

    shops.forEach(function (shop) {
      const normalized = normalizeShop(shop, shop && shop.area_id);
      if (!normalized) return;
      if (seen[normalized.id]) return;
      seen[normalized.id] = true;
      merged.push(normalized);
    });

    return merged;
  }

  function normalizeShop(raw, fallbackAreaId) {
    if (!raw || typeof raw !== "object") return null;

    const areaId = resolveAreaId(raw.area_id || fallbackAreaId);
    const name = cleanText(raw.name, 40);
    if (!name) return null;

    const id = toCleanId(raw.id) || createId("shop");
    return {
      id: id,
      name: name,
      area_id: areaId,
      note: cleanText(raw.note, 100),
      created_by: cleanText(raw.created_by, 30),
      created_at:
        typeof raw.created_at === "string" && raw.created_at
          ? raw.created_at
          : new Date().toISOString(),
    };
  }

  function normalizeRatings(ratings) {
    if (!Array.isArray(ratings)) return [];
    const normalized = [];
    ratings.forEach(function (entry) {
      if (!entry || typeof entry !== "object") return;
      const shopId = cleanText(entry.shop_id || entry.shopId, 80);
      const score = Number(entry.score);
      if (!shopId || !Number.isFinite(score)) return;
      const rounded = Math.round(score);
      if (rounded < 1 || rounded > 5) return;

      normalized.push({
        id: toCleanId(entry.id) || createId("rating"),
        shop_id: shopId,
        score: rounded,
        reviewer: cleanText(entry.reviewer || entry.user, 30),
        created_at:
          typeof entry.created_at === "string" && entry.created_at
            ? entry.created_at
            : new Date().toISOString(),
      });
    });
    return normalized;
  }

  function resolveAreaId(candidate) {
    const clean = toCleanId(candidate);
    if (clean && areaMap[clean]) return clean;
    return REQUIRED_AREAS[0].id;
  }

  function toCleanId(value) {
    if (typeof value !== "string") return "";
    return value.trim().replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 80);
  }

  function cleanText(value, maxLength) {
    if (typeof value !== "string") return "";
    return value.trim().replace(/\s+/g, " ").slice(0, maxLength);
  }

  function createId(prefix) {
    return (
      prefix +
      "-" +
      Date.now().toString(36) +
      "-" +
      Math.random().toString(36).slice(2, 7)
    );
  }

  function buildStats() {
    const stats = {};
    state.shops.forEach(function (shop) {
      stats[shop.id] = { sum: 0, count: 0 };
    });

    state.ratings.forEach(function (rating) {
      if (!stats[rating.shop_id]) return;
      stats[rating.shop_id].sum += rating.score;
      stats[rating.shop_id].count += 1;
    });
    return stats;
  }

  function getSortedShops(stats) {
    return state.shops
      .slice()
      .sort(function (a, b) {
        const aBucket = stats[a.id];
        const bBucket = stats[b.id];
        const aAvg = aBucket.count ? aBucket.sum / aBucket.count : -1;
        const bAvg = bBucket.count ? bBucket.sum / bBucket.count : -1;

        if (bAvg !== aAvg) return bAvg - aAvg;
        if (bBucket.count !== aBucket.count) return bBucket.count - aBucket.count;
        return a.name.localeCompare(b.name, "zh-Hans-CN");
      });
  }

  function formatAvg(bucket) {
    if (!bucket || !bucket.count) return "--";
    return (bucket.sum / bucket.count).toFixed(2);
  }

  function renderAll() {
    renderMode();
    renderShopSelect();
    renderRankingTable();
    renderAreaGrid();
  }

  function renderMode() {
    if (!ui.mode) return;
    ui.mode.className =
      "food-board-mode " + (storeMode === "remote" ? "is-remote" : "is-local");
    ui.mode.textContent = storeModeMessage;
  }

  function renderRankingTable() {
    if (!ui.rankingBody) return;
    ui.rankingBody.innerHTML = "";

    const stats = buildStats();
    const ordered = getSortedShops(stats);

    if (!ordered.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 5;
      cell.textContent = "暂无店铺，请先添加。";
      row.appendChild(cell);
      ui.rankingBody.appendChild(row);
      return;
    }

    ordered.forEach(function (shop, index) {
      const row = document.createElement("tr");
      const bucket = stats[shop.id];
      const area = areaMap[shop.area_id];

      row.appendChild(createCell(String(index + 1)));
      row.appendChild(createCell(shop.name));
      row.appendChild(createCell(area ? area.name : shop.area_id));
      row.appendChild(createCell(formatAvg(bucket)));
      row.appendChild(createCell(String(bucket ? bucket.count : 0)));
      ui.rankingBody.appendChild(row);
    });
  }

  function createCell(text) {
    const cell = document.createElement("td");
    cell.textContent = text;
    return cell;
  }

  function renderShopSelect() {
    if (!ui.ratingShop) return;
    ui.ratingShop.innerHTML = "";

    areas.forEach(function (area) {
      const group = document.createElement("optgroup");
      group.label = area.name;

      state.shops
        .filter(function (shop) {
          return shop.area_id === area.id;
        })
        .sort(function (a, b) {
          return a.name.localeCompare(b.name, "zh-Hans-CN");
        })
        .forEach(function (shop) {
          const option = document.createElement("option");
          option.value = shop.id;
          option.textContent = shop.name;
          group.appendChild(option);
        });

      if (group.children.length) {
        ui.ratingShop.appendChild(group);
      }
    });

    if (!ui.ratingShop.options.length) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "请先添加店铺";
      ui.ratingShop.appendChild(option);
    }
  }

  function renderAreaGrid() {
    if (!ui.areaGrid) return;
    ui.areaGrid.innerHTML = "";

    const stats = buildStats();
    areas.forEach(function (area) {
      const card = document.createElement("article");
      card.className = "food-area-card";

      const title = document.createElement("h3");
      title.textContent = area.name;
      card.appendChild(title);

      const list = document.createElement("ul");
      list.className = "food-area-shop-list";

      const shopsInArea = state.shops
        .filter(function (shop) {
          return shop.area_id === area.id;
        })
        .sort(function (a, b) {
          const aBucket = stats[a.id];
          const bBucket = stats[b.id];
          const aAvg = aBucket.count ? aBucket.sum / aBucket.count : -1;
          const bAvg = bBucket.count ? bBucket.sum / bBucket.count : -1;
          if (bAvg !== aAvg) return bAvg - aAvg;
          return a.name.localeCompare(b.name, "zh-Hans-CN");
        });

      if (!shopsInArea.length) {
        const empty = document.createElement("li");
        empty.className = "food-area-empty";
        empty.textContent = "暂无店铺，欢迎添加。";
        list.appendChild(empty);
      } else {
        shopsInArea.forEach(function (shop) {
          const bucket = stats[shop.id];
          const item = document.createElement("li");
          item.className = "food-area-shop";

          const top = document.createElement("div");
          top.className = "food-area-shop-top";
          const name = document.createElement("strong");
          name.textContent = shop.name;
          top.appendChild(name);

          const quickRate = document.createElement("button");
          quickRate.type = "button";
          quickRate.className = "food-quick-rate-btn";
          quickRate.setAttribute("data-shop-id", shop.id);
          quickRate.textContent = "去评分";
          top.appendChild(quickRate);
          item.appendChild(top);

          const meta = document.createElement("p");
          meta.className = "food-area-shop-meta";
          meta.textContent =
            "均值: " +
            formatAvg(bucket) +
            " | 评分数: " +
            String(bucket ? bucket.count : 0);
          item.appendChild(meta);

          if (shop.note) {
            const note = document.createElement("p");
            note.className = "food-area-shop-note";
            note.textContent = shop.note;
            item.appendChild(note);
          }

          list.appendChild(item);
        });
      }

      card.appendChild(list);
      ui.areaGrid.appendChild(card);
    });
  }

  function hydrateAreaSelect() {
    if (!ui.addShopArea) return;
    ui.addShopArea.innerHTML = "";
    areas.forEach(function (area) {
      const option = document.createElement("option");
      option.value = area.id;
      option.textContent = area.name;
      ui.addShopArea.appendChild(option);
    });
  }

  function bindEvents() {
    if (ui.ratingForm) {
      ui.ratingForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearMessage(ui.ratingMessage);

        const shopId = cleanText(ui.ratingShop.value, 80);
        const score = Number(ui.ratingScore.value);
        const reviewer = cleanText(ui.ratingUser.value, 30);
        const shopExists = state.shops.some(function (shop) {
          return shop.id === shopId;
        });

        if (!shopExists) {
          setMessage(ui.ratingMessage, "请选择有效店铺。", "error");
          return;
        }
        if (!Number.isInteger(score) || score < 1 || score > 5) {
          setMessage(ui.ratingMessage, "评分仅支持 1 到 5。", "error");
          return;
        }

        const newRating = {
          id: createId("rating"),
          shop_id: shopId,
          score: score,
          reviewer: reviewer,
          created_at: new Date().toISOString(),
        };

        setFormDisabled(ui.ratingSubmit, true);
        try {
          if (storeMode === "remote") {
            await writeRemoteItem("ratings", newRating);
          }
          state.ratings.push(newRating);
          saveLocalState();
          renderAll();
          setMessage(ui.ratingMessage, "评分已提交，榜单已更新。", "success");
          ui.ratingForm.reset();
          ui.ratingScore.value = "5";
        } catch (_) {
          setMessage(ui.ratingMessage, "提交失败，请稍后重试。", "error");
        } finally {
          setFormDisabled(ui.ratingSubmit, false);
        }
      });
    }

    if (ui.addShopForm) {
      ui.addShopForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearMessage(ui.addShopMessage);

        const areaId = resolveAreaId(ui.addShopArea.value);
        const name = cleanText(ui.addShopName.value, 40);
        const owner = cleanText(ui.addShopOwner.value, 30);

        if (!name) {
          setMessage(ui.addShopMessage, "请填写店铺名。", "error");
          return;
        }

        const duplicated = state.shops.some(function (shop) {
          return (
            shop.area_id === areaId &&
            shop.name.toLowerCase() === name.toLowerCase()
          );
        });
        if (duplicated) {
          setMessage(ui.addShopMessage, "该区域已存在同名店铺。", "error");
          return;
        }

        const newShop = {
          id: createId("shop"),
          name: name,
          area_id: areaId,
          created_by: owner,
          created_at: new Date().toISOString(),
        };

        setFormDisabled(ui.addShopSubmit, true);
        try {
          if (storeMode === "remote") {
            await writeRemoteItem("shops", newShop);
          }
          state.shops.push(newShop);
          saveLocalState();
          renderAll();
          setMessage(ui.addShopMessage, "店铺已添加。", "success");
          ui.addShopForm.reset();
          ui.addShopArea.value = areaId;
        } catch (_) {
          setMessage(ui.addShopMessage, "添加失败，请稍后重试。", "error");
        } finally {
          setFormDisabled(ui.addShopSubmit, false);
        }
      });
    }

    if (ui.areaGrid) {
      ui.areaGrid.addEventListener("click", function (event) {
        const target = event.target;
        if (!target || !target.matches("button[data-shop-id]")) return;
        const shopId = target.getAttribute("data-shop-id");
        if (!shopId || !ui.ratingShop) return;
        ui.ratingShop.value = shopId;

        const rateSection = document.getElementById("food-board-rate");
        if (rateSection) {
          rateSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    }
  }

  function setFormDisabled(button, disabled) {
    if (!button) return;
    button.disabled = disabled;
  }

  function setMessage(element, text, type) {
    if (!element) return;
    element.className = "food-board-message is-" + type;
    element.textContent = text;
  }

  function clearMessage(element) {
    if (!element) return;
    element.className = "food-board-message";
    element.textContent = "";
  }

  function initSmoothAnchor() {
    document
      .querySelectorAll(".food-board-inline-toc a[href^='#']")
      .forEach(function (anchor) {
        anchor.addEventListener("click", function (event) {
          const href = anchor.getAttribute("href");
          if (!href) return;
          const target = document.querySelector(href);
          if (!target) return;
          event.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      });
  }
})();
