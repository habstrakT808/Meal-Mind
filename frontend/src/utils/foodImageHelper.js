/**
 * Database gambar makanan yang sesuai dengan nama makanan
 * Kata kunci dalam nama makanan akan dicocokkan dengan gambar yang sesuai
 */
const foodImageDatabase = {
  // Makanan Sarapan
  "nasi gudeg":
    "https://images.unsplash.com/photo-1569058242567-93de6f36f8eb?w=500&auto=format",
  telur:
    "https://images.unsplash.com/photo-1607690424560-35d67da0e775?w=500&auto=format",
  "roti bakar":
    "https://images.unsplash.com/photo-1590368746679-a403ad57e691?w=500&auto=format",
  selai:
    "https://images.unsplash.com/photo-1615839170192-33dc5a9025e6?w=500&auto=format",
  susu: "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=500&auto=format",
  "bubur ayam":
    "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=500&auto=format",
  kerupuk:
    "https://images.unsplash.com/photo-1581512798625-8c840516f02c?w=500&auto=format",
  "nasi uduk":
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format",
  "ayam goreng":
    "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=500&auto=format",
  "lontong sayur":
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format",
  oatmeal:
    "https://images.unsplash.com/photo-1614961233913-a5113a4a34ed?w=500&auto=format",
  pisang:
    "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=500&auto=format",
  pancake:
    "https://images.unsplash.com/photo-1558401391-67e4829e16e3?w=500&auto=format",
  madu: "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=500&auto=format",
  "nasi goreng":
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format",
  sereal:
    "https://images.unsplash.com/photo-1521483451569-e33803c3378a?w=500&auto=format",
  "telur dadar":
    "https://images.unsplash.com/photo-1607690424560-35d67da0e775?w=500&auto=format",
  sandwich:
    "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500&auto=format",
  keju: "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=500&auto=format",
  yogurt:
    "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&auto=format",
  granola:
    "https://images.unsplash.com/photo-1590301157890-4810ed352733?w=500&auto=format",
  alpukat:
    "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=500&auto=format",
  "pisang goreng":
    "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=500&auto=format",
  teh: "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&auto=format",
  ketupat:
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format",

  // Makanan Makan Siang
  "ayam bakar":
    "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=500&auto=format",
  lalapan:
    "https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=500&auto=format",
  rendang:
    "https://images.unsplash.com/photo-1606491048802-8342506d6471?w=500&auto=format",
  sayur:
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "ikan bakar":
    "https://images.unsplash.com/photo-1603073143333-a3a6c824e963?w=500&auto=format",
  "tumis kangkung":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "soto ayam":
    "https://images.unsplash.com/photo-1583592643761-bf2ecd1ae43f?w=500&auto=format",
  "gado-gado":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  pecel:
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  tempe:
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
  "mie goreng":
    "https://images.unsplash.com/photo-1633872427779-1da2e3b8e891?w=500&auto=format",
  "sayur asem":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "tempe goreng":
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
  rawon:
    "https://images.unsplash.com/photo-1583592643761-bf2ecd1ae43f?w=500&auto=format",
  "sate ayam":
    "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=500&auto=format",
  "sambal kacang":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "bakso kuah":
    "https://images.unsplash.com/photo-1583592643761-bf2ecd1ae43f?w=500&auto=format",
  mie: "https://images.unsplash.com/photo-1633872427779-1da2e3b8e891?w=500&auto=format",
  "gulai ikan":
    "https://images.unsplash.com/photo-1621937946271-e8a951d61b11?w=500&auto=format",
  "ayam pop":
    "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=500&auto=format",
  "tahu telor":
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
  sambal:
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  capcay:
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  seafood:
    "https://images.unsplash.com/photo-1573506254685-02bcafee8071?w=500&auto=format",

  // Makanan Makan Malam
  "pecel lele":
    "https://images.unsplash.com/photo-1621937946271-e8a951d61b11?w=500&auto=format",
  "ayam geprek":
    "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=500&auto=format",
  "mie ayam":
    "https://images.unsplash.com/photo-1633872427779-1da2e3b8e891?w=500&auto=format",
  pangsit:
    "https://images.unsplash.com/photo-1583032015879-e5022cb87c3b?w=500&auto=format",
  bakso:
    "https://images.unsplash.com/photo-1583592643761-bf2ecd1ae43f?w=500&auto=format",
  "tahu telur":
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
  "oseng kangkung":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "ikan asin":
    "https://images.unsplash.com/photo-1573506254685-02bcafee8071?w=500&auto=format",
  "terong balado":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "sup ayam":
    "https://images.unsplash.com/photo-1583592643761-bf2ecd1ae43f?w=500&auto=format",
  ketoprak:
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "teh manis":
    "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&auto=format",
  "bihun goreng":
    "https://images.unsplash.com/photo-1633872427779-1da2e3b8e891?w=500&auto=format",
  "rica-rica":
    "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=500&auto=format",
  "cakalang fufu":
    "https://images.unsplash.com/photo-1573506254685-02bcafee8071?w=500&auto=format",
  "telur balado":
    "https://images.unsplash.com/photo-1607690424560-35d67da0e775?w=500&auto=format",
  sup: "https://images.unsplash.com/photo-1583592643761-bf2ecd1ae43f?w=500&auto=format",
  lontong:
    "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format",
  "gulai sayur":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",
  "tongkol balado":
    "https://images.unsplash.com/photo-1573506254685-02bcafee8071?w=500&auto=format",
  "tumis kacang":
    "https://images.unsplash.com/photo-1603048503899-32524a71b551?w=500&auto=format",

  // Makanan Ringan
  "roti kering":
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format",
  "kacang tanah":
    "https://images.unsplash.com/photo-1567892737950-30fd8f4fb3c0?w=500&auto=format",
  "keripik singkong":
    "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=500&auto=format",
  "tempe mendoan":
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
  "ubi rebus":
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
  "telur rebus":
    "https://images.unsplash.com/photo-1607690424560-35d67da0e775?w=500&auto=format",
  "roti panggang":
    "https://images.unsplash.com/photo-1590368746679-a403ad57e691?w=500&auto=format",
  jeruk:
    "https://images.unsplash.com/photo-1580052614034-c55d20bfee3b?w=500&auto=format",
  "keripik tempe":
    "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",

  // Makanan Western
  burger:
    "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format",
  "kentang goreng":
    "https://images.unsplash.com/photo-1585109649139-366815a0d713?w=500&auto=format",
  pizza:
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format",
  pasta:
    "https://images.unsplash.com/photo-1516100882582-96c3a05fe590?w=500&auto=format",
  carbonara:
    "https://images.unsplash.com/photo-1516100882582-96c3a05fe590?w=500&auto=format",
  "caesar salad":
    "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=500&auto=format",
  tuna: "https://images.unsplash.com/photo-1573506254685-02bcafee8071?w=500&auto=format",
  steak:
    "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=500&auto=format",
  "daging sapi":
    "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=500&auto=format",
  kentang:
    "https://images.unsplash.com/photo-1552661397-4233881773f9?w=500&auto=format",
  "fish & chips":
    "https://images.unsplash.com/photo-1579636858001-47d95599a5d5?w=500&auto=format",
  burrito:
    "https://images.unsplash.com/photo-1584208632869-05fa2b2a5934?w=500&auto=format",

  // Makanan Sehat
  salad:
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format",
  "ayam panggang":
    "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=500&auto=format",
  quinoa:
    "https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?w=500&auto=format",
  salmon:
    "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500&auto=format",
  smoothie:
    "https://images.unsplash.com/photo-1502741224143-90386d7f8c82?w=500&auto=format",
  kacang:
    "https://images.unsplash.com/photo-1567892737950-30fd8f4fb3c0?w=500&auto=format",
  buah: "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=500&auto=format",
  wrap: "https://images.unsplash.com/photo-1600850056064-a8b380df8395?w=500&auto=format",
  hummus:
    "https://images.unsplash.com/photo-1637949385162-10de67cc9514?w=500&auto=format",
  "buddha bowl":
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format",
  tofu: "https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=500&auto=format",
};

// Placeholder default untuk gambar yang tidak ditemukan
const DEFAULT_FOOD_IMAGE = {
  Breakfast:
    "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=500&auto=format",
  Lunch:
    "https://images.unsplash.com/photo-1586511925558-a4c6376fe65f?w=500&auto=format",
  Dinner:
    "https://images.unsplash.com/photo-1576866209830-589e1bfbaa04?w=500&auto=format",
  Snack:
    "https://images.unsplash.com/photo-1619546952812-520e98064a52?w=500&auto=format",
  default:
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&auto=format",
};

/**
 * Fungsi untuk mendapatkan gambar makanan berdasarkan nama
 * @param {string} foodName - Nama makanan
 * @param {string} mealType - Jenis makanan (Breakfast, Lunch, Dinner, Snack)
 * @returns {string} URL gambar makanan
 */
export const getFoodImage = (foodName, mealType = "default") => {
  // Jika tidak ada nama makanan, gunakan gambar default berdasarkan jenis makanan
  if (!foodName) {
    return DEFAULT_FOOD_IMAGE[mealType] || DEFAULT_FOOD_IMAGE.default;
  }

  // Ubah ke lowercase untuk pencocokan yang lebih baik
  const foodNameLower = foodName.toLowerCase();

  // Pecah nama makanan menjadi kata-kata
  const words = foodNameLower.split(/\s+|[+]|\dengan/);

  // Cari kata kunci yang cocok dalam database gambar
  for (const keyword of Object.keys(foodImageDatabase)) {
    // Cek apakah ada kata dalam nama makanan yang cocok dengan keyword
    for (const word of words) {
      if (word.length > 2 && keyword.toLowerCase().includes(word)) {
        return foodImageDatabase[keyword];
      }
    }
  }

  // Cek jika makanan mengandung keyword yang ada di database
  for (const keyword of Object.keys(foodImageDatabase)) {
    if (foodNameLower.includes(keyword.toLowerCase())) {
      return foodImageDatabase[keyword];
    }
  }

  // Jika tidak ditemukan, gunakan gambar default
  return DEFAULT_FOOD_IMAGE[mealType] || DEFAULT_FOOD_IMAGE.default;
};

// Fungsi untuk memeriksa ketersediaan gambar
export const checkImageAvailability = async (url) => {
  // Jika tidak ada URL, gambar tidak tersedia
  if (!url) return false;

  try {
    const response = await fetch(url, { method: "HEAD" });
    return response.ok;
  } catch (error) {
    console.error("Error checking image availability:", error);
    return false;
  }
};

// Fungsi untuk mendapatkan placeholder gambar berdasarkan jenis makanan
export const getPlaceholderImage = (mealType) => {
  switch (mealType) {
    case "Breakfast":
      return "🍳";
    case "Lunch":
      return "🍲";
    case "Dinner":
      return "🍽️";
    case "Snack":
      return "🥨";
    default:
      return "🍔";
  }
};

export default {
  getFoodImage,
  checkImageAvailability,
  getPlaceholderImage,
};
