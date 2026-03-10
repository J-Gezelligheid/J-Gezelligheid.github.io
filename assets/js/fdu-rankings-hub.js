(function () {
  const seedEl = document.getElementById("rankings-hub-seed");
  if (!seedEl) return;

  const AREA_FALLBACK = {
    "guoquan-road": "国权路",
    "sanhao-bay": "三号湾",
    wujiaochang: "五角场",
  };

  let seed = { boards: [] };
  try {
    seed = JSON.parse(seedEl.textContent || "{}");
  } catch (_) {
    seed = { boards: [] };
  }

  const boards = Array.isArray(seed.boards) ? seed.boards : [];
  if (!boards.length) return;

  initSmoothAnchor();
  loadAllBoards();

  async function loadAllBoards() {
    await Promise.all(
      boards.map(async function (board) {
        await loadOneBoard(board);
      })
    );
  }

  async function loadOneBoard(board) {
    const key = cleanKey(board && board.key);
    if (!key) return;

    const boardData = board && board.data ? board.data : {};
    const firebase = normalizeFirebaseConfig(boardData.firebase);
    const areas = normalizeAreas(boardData.areas);
    const seedShops = buildSeedShops(areas);

    let persisted = { shops: [], ratings: [] };
    let stateText = "本地种子数据";

    if (firebase.enabled) {
      try {
        persisted = await fetchRemoteBoard(firebase);
        stateText = "Firebase 共享数据";
      } catch (_) {
        stateText = "Firebase 拉取失败，展示种子数据";
      }
    }

    const mergedShops = mergeShops(seedShops.concat(persisted.shops || []));
    const shopIdSet = new Set(
      mergedShops.map(function (shop) {
        return shop.id;
      })
    );
    const ratings = normalizeRatings(persisted.ratings || []).filter(function (
      rating
    ) {
      return shopIdSet.has(rating.shop_id);
    });

    renderBoard(key, mergedShops, ratings, areas, stateText, boardData.updated_at);
  }

  function renderBoard(key, shops, ratings, areas, stateText, updatedAt) {
    const tbody = document.getElementById("hub-table-" + key);
    const stateEl = document.getElementById("hub-state-" + key);
    const updatedEl = document.getElementById("hub-updated-" + key);
    if (!tbody || !stateEl || !updatedEl) return;

    stateEl.textContent = stateText;
    updatedEl.textContent = typeof updatedAt === "string" ? updatedAt : "--";
    tbody.innerHTML = "";

    const areaMap = {};
    areas.forEach(function (area) {
      areaMap[area.id] = area.name;
    });

    const stats = buildStats(shops, ratings);
    const orderedShops = shops
      .slice()
      .sort(function (a, b) {
        const aAvg = stats[a.id].count ? stats[a.id].sum / stats[a.id].count : -1;
        const bAvg = stats[b.id].count ? stats[b.id].sum / stats[b.id].count : -1;
        if (bAvg !== aAvg) return bAvg - aAvg;
        if (stats[b.id].count !== stats[a.id].count) {
          return stats[b.id].count - stats[a.id].count;
        }
        return a.name.localeCompare(b.name, "zh-Hans-CN");
      });

    if (!orderedShops.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 5;
      cell.textContent = "暂无店铺。";
      row.appendChild(cell);
      tbody.appendChild(row);
      return;
    }

    orderedShops.forEach(function (shop, index) {
      const row = document.createElement("tr");
      const bucket = stats[shop.id];

      row.appendChild(createCell(String(index + 1)));
      row.appendChild(createCell(shop.name));
      row.appendChild(createCell(areaMap[shop.area_id] || shop.area_id));
      row.appendChild(createCell(bucket.count ? (bucket.sum / bucket.count).toFixed(2) : "--"));
      row.appendChild(createCell(String(bucket.count)));
      tbody.appendChild(row);
    });
  }

  function buildStats(shops, ratings) {
    const stats = {};
    shops.forEach(function (shop) {
      stats[shop.id] = { sum: 0, count: 0 };
    });
    ratings.forEach(function (rating) {
      if (!stats[rating.shop_id]) return;
      stats[rating.shop_id].sum += rating.score;
      stats[rating.shop_id].count += 1;
    });
    return stats;
  }

  function createCell(text) {
    const cell = document.createElement("td");
    cell.textContent = text;
    return cell;
  }

  async function fetchRemoteBoard(firebase) {
    const url =
      firebase.databaseUrl.replace(/\/+$/, "") +
      "/" +
      firebase.dataRoot +
      ".json";
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Failed to read remote board.");
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

  function normalizeFirebaseConfig(raw) {
    if (!raw || typeof raw !== "object") {
      return {
        enabled: false,
        databaseUrl: "",
        dataRoot: "",
      };
    }

    const databaseUrl =
      typeof raw.database_url === "string" ? raw.database_url.trim() : "";
    const dataRoot =
      typeof raw.data_root === "string" ? raw.data_root.trim().replace(/^\/+|\/+$/g, "") : "";
    const enabled =
      raw.enabled === true &&
      databaseUrl &&
      dataRoot &&
      !isPlaceholder(databaseUrl);

    return {
      enabled: enabled,
      databaseUrl: databaseUrl,
      dataRoot: dataRoot,
    };
  }

  function isPlaceholder(value) {
    if (typeof value !== "string") return false;
    const upper = value.toUpperCase();
    return upper.indexOf("REPLACE_WITH_") !== -1;
  }

  function normalizeRemoteCollection(payload, includeIdFromKey) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== "object") return [];
    return Object.keys(payload)
      .map(function (key) {
        const item = payload[key];
        if (!item || typeof item !== "object") return null;
        const copy = Object.assign({}, item);
        if (includeIdFromKey && !copy.id) copy.id = key;
        return copy;
      })
      .filter(Boolean);
  }

  function normalizeAreas(rawAreas) {
    const areaById = {};
    if (Array.isArray(rawAreas)) {
      rawAreas.forEach(function (area) {
        if (!area || typeof area !== "object") return;
        const id = cleanId(area.id);
        if (!id) return;
        areaById[id] = {
          id: id,
          name:
            typeof area.name === "string" && area.name.trim()
              ? area.name.trim()
              : AREA_FALLBACK[id] || id,
          shops: Array.isArray(area.shops) ? area.shops : [],
        };
      });
    }

    return Object.keys(AREA_FALLBACK).map(function (id) {
      return areaById[id] || { id: id, name: AREA_FALLBACK[id], shops: [] };
    });
  }

  function buildSeedShops(areas) {
    const shops = [];
    areas.forEach(function (area) {
      area.shops.forEach(function (shop) {
        const normalized = normalizeShop(shop, area.id);
        if (normalized) shops.push(normalized);
      });
    });
    return mergeShops(shops);
  }

  function mergeShops(shops) {
    const merged = [];
    const seen = {};
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
    const id = cleanId(raw.id);
    const name = cleanText(raw.name, 40);
    const areaId = cleanId(raw.area_id || fallbackAreaId);
    if (!id || !name || !areaId) return null;
    return {
      id: id,
      name: name,
      area_id: areaId,
    };
  }

  function normalizeRatings(rawRatings) {
    if (!Array.isArray(rawRatings)) return [];
    return rawRatings
      .map(function (rating) {
        if (!rating || typeof rating !== "object") return null;
        const shopId = cleanText(rating.shop_id || rating.shopId, 80);
        const score = Number(rating.score);
        if (!shopId || !Number.isFinite(score)) return null;
        const rounded = Math.round(score);
        if (rounded < 1 || rounded > 5) return null;
        return {
          shop_id: shopId,
          score: rounded,
        };
      })
      .filter(Boolean);
  }

  function cleanId(value) {
    if (typeof value !== "string") return "";
    return value.trim().replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 80);
  }

  function cleanText(value, maxLen) {
    if (typeof value !== "string") return "";
    return value.trim().replace(/\s+/g, " ").slice(0, maxLen);
  }

  function cleanKey(value) {
    if (typeof value !== "string") return "";
    return value.trim().replace(/[^a-z0-9_-]/gi, "");
  }

  function initSmoothAnchor() {
    document
      .querySelectorAll(".rankings-hub-toc a[href^='#']")
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
