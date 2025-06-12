/**
 * Database gambar aktivitas yang sesuai dengan nama aktivitas
 * Kata kunci dalam nama aktivitas akan dicocokkan dengan gambar yang sesuai
 */
const activityImageDatabase = {
  // Cardio
  "lari pagi":
    "https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=500&auto=format",
  jogging:
    "https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=500&auto=format",
  lari: "https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=500&auto=format",
  "lari santai":
    "https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=500&auto=format",
  marathon:
    "https://images.unsplash.com/photo-1600055882386-5d18b02a0d51?w=500&auto=format",
  sprinting:
    "https://images.unsplash.com/photo-1520367691844-3df6689218c6?w=500&auto=format",
  bersepeda:
    "https://images.unsplash.com/photo-1526395050546-dc5b0fe8df5f?w=500&auto=format",
  sepeda:
    "https://images.unsplash.com/photo-1526395050546-dc5b0fe8df5f?w=500&auto=format",
  "bersepeda santai":
    "https://images.unsplash.com/photo-1526395050546-dc5b0fe8df5f?w=500&auto=format",
  "sepeda statis":
    "https://images.unsplash.com/photo-1596215436617-9598e7365efa?w=500&auto=format",
  spinning:
    "https://images.unsplash.com/photo-1596215436617-9598e7365efa?w=500&auto=format",
  berenang:
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  renang:
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "renang gaya bebas":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "berenang gaya bebas":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "renang gaya dada":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "berenang gaya dada":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "jumping jacks":
    "https://images.unsplash.com/photo-1616279969856-759f559ac222?w=500&auto=format",
  "skipping rope":
    "https://images.unsplash.com/photo-1599058918144-1ffabb6ab9a0?w=500&auto=format",
  "lompat tali":
    "https://images.unsplash.com/photo-1599058918144-1ffabb6ab9a0?w=500&auto=format",
  "skip rope":
    "https://images.unsplash.com/photo-1599058918144-1ffabb6ab9a0?w=500&auto=format",
  "lompat-lompat":
    "https://images.unsplash.com/photo-1599058918144-1ffabb6ab9a0?w=500&auto=format",
  kardio:
    "https://images.unsplash.com/photo-1640068505824-2eed42dab972?w=500&auto=format",
  cardio:
    "https://images.unsplash.com/photo-1640068505824-2eed42dab972?w=500&auto=format",
  hiking:
    "https://images.unsplash.com/photo-1539183204366-63a0589187ab?w=500&auto=format",
  mendaki:
    "https://images.unsplash.com/photo-1539183204366-63a0589187ab?w=500&auto=format",
  jalan:
    "https://images.unsplash.com/photo-1487956382158-bb926046304a?w=500&auto=format",
  "jalan kaki":
    "https://images.unsplash.com/photo-1487956382158-bb926046304a?w=500&auto=format",
  "jalan santai":
    "https://images.unsplash.com/photo-1487956382158-bb926046304a?w=500&auto=format",
  "jalan pagi":
    "https://images.unsplash.com/photo-1487956382158-bb926046304a?w=500&auto=format",
  "jalan sore":
    "https://images.unsplash.com/photo-1487956382158-bb926046304a?w=500&auto=format",
  "power walking":
    "https://images.unsplash.com/photo-1483721310020-03333e577078?w=500&auto=format",
  "elliptical training":
    "https://images.unsplash.com/photo-1562771379-eafdca7a02f8?w=500&auto=format",
  "stair climbing":
    "https://images.unsplash.com/photo-1605296867724-fa87a8ef53fd?w=500&auto=format",
  "naik tangga":
    "https://images.unsplash.com/photo-1605296867724-fa87a8ef53fd?w=500&auto=format",
  "menaiki tangga":
    "https://images.unsplash.com/photo-1605296867724-fa87a8ef53fd?w=500&auto=format",
  rowing:
    "https://images.unsplash.com/photo-1607962837359-5e7e89f86776?w=500&auto=format",
  mendayung:
    "https://images.unsplash.com/photo-1607962837359-5e7e89f86776?w=500&auto=format",

  // Latihan Kekuatan (Strength Training)
  "push-up":
    "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=500&auto=format",
  pushup:
    "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=500&auto=format",
  "push up":
    "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=500&auto=format",
  "sit-up":
    "https://images.unsplash.com/photo-1544216717-3bbf52512659?w=500&auto=format",
  situp:
    "https://images.unsplash.com/photo-1544216717-3bbf52512659?w=500&auto=format",
  "sit up":
    "https://images.unsplash.com/photo-1544216717-3bbf52512659?w=500&auto=format",
  "pull-up":
    "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=500&auto=format",
  pullup:
    "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=500&auto=format",
  "pull up":
    "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=500&auto=format",
  squat:
    "https://images.unsplash.com/photo-1566241142248-11865261e779?w=500&auto=format",
  "bodyweight squat":
    "https://images.unsplash.com/photo-1566241142248-11865261e779?w=500&auto=format",
  squats:
    "https://images.unsplash.com/photo-1566241142248-11865261e779?w=500&auto=format",
  lunges:
    "https://images.unsplash.com/photo-1584863231364-2edc166de576?w=500&auto=format",
  lunge:
    "https://images.unsplash.com/photo-1584863231364-2edc166de576?w=500&auto=format",
  planks:
    "https://images.unsplash.com/photo-1614928228253-dc09cbc3b11c?w=500&auto=format",
  plank:
    "https://images.unsplash.com/photo-1614928228253-dc09cbc3b11c?w=500&auto=format",
  crunches:
    "https://images.unsplash.com/photo-1544216717-3bbf52512659?w=500&auto=format",
  crunch:
    "https://images.unsplash.com/photo-1544216717-3bbf52512659?w=500&auto=format",
  dips: "https://images.unsplash.com/photo-1588347809802-73cb4520e784?w=500&auto=format",
  dip: "https://images.unsplash.com/photo-1588347809802-73cb4520e784?w=500&auto=format",
  "bench press":
    "https://images.unsplash.com/photo-1517344368193-41552b6ad3f5?w=500&auto=format",
  "bench-press":
    "https://images.unsplash.com/photo-1517344368193-41552b6ad3f5?w=500&auto=format",
  benchpress:
    "https://images.unsplash.com/photo-1517344368193-41552b6ad3f5?w=500&auto=format",
  "press dada":
    "https://images.unsplash.com/photo-1517344368193-41552b6ad3f5?w=500&auto=format",
  "chest press":
    "https://images.unsplash.com/photo-1517344368193-41552b6ad3f5?w=500&auto=format",
  deadlift:
    "https://images.unsplash.com/photo-1596357395217-80de13130e92?w=500&auto=format",
  "dead-lift":
    "https://images.unsplash.com/photo-1596357395217-80de13130e92?w=500&auto=format",
  "dead lift":
    "https://images.unsplash.com/photo-1596357395217-80de13130e92?w=500&auto=format",
  "overhead press":
    "https://images.unsplash.com/photo-1597347316205-36f6c451902a?w=500&auto=format",
  "military press":
    "https://images.unsplash.com/photo-1597347316205-36f6c451902a?w=500&auto=format",
  "shoulder press":
    "https://images.unsplash.com/photo-1597347316205-36f6c451902a?w=500&auto=format",
  rows: "https://images.unsplash.com/photo-1539794830467-1f1755804d13?w=500&auto=format",
  row: "https://images.unsplash.com/photo-1539794830467-1f1755804d13?w=500&auto=format",
  "barbell row":
    "https://images.unsplash.com/photo-1539794830467-1f1755804d13?w=500&auto=format",
  "dumbbell row":
    "https://images.unsplash.com/photo-1539794830467-1f1755804d13?w=500&auto=format",
  "leg press":
    "https://images.unsplash.com/photo-1581122584612-713f89daa8eb?w=500&auto=format",
  "leg-press":
    "https://images.unsplash.com/photo-1581122584612-713f89daa8eb?w=500&auto=format",
  legpress:
    "https://images.unsplash.com/photo-1581122584612-713f89daa8eb?w=500&auto=format",
  "shoulder exercise":
    "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=500&auto=format",
  "latihan bahu":
    "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=500&auto=format",
  "bicep curls":
    "https://images.unsplash.com/photo-1581009137042-c552e485697a?w=500&auto=format",
  "bicep curl":
    "https://images.unsplash.com/photo-1581009137042-c552e485697a?w=500&auto=format",
  curl: "https://images.unsplash.com/photo-1581009137042-c552e485697a?w=500&auto=format",
  "angkat beban":
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  "weight lifting":
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  weightlifting:
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  "strength training":
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  "latihan kekuatan":
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  gym: "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  "weight training":
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  "resistance training":
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format",
  "fitness training":
    "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format",
  fitness:
    "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format",

  // Latihan Fleksibilitas (Flexibility)
  yoga: "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=500&auto=format",
  "yoga flow":
    "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=500&auto=format",
  "latihan yoga":
    "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=500&auto=format",
  pilates:
    "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format",
  peregangan:
    "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=500&auto=format",
  stretching:
    "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=500&auto=format",
  stretch:
    "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=500&auto=format",
  "gerakan peregangan":
    "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=500&auto=format",
  "dynamic stretching":
    "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=500&auto=format",
  "static stretching":
    "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=500&auto=format",
  "tai chi":
    "https://images.unsplash.com/photo-1560253414-d6535ae78f2c?w=500&auto=format",
  taichi:
    "https://images.unsplash.com/photo-1560253414-d6535ae78f2c?w=500&auto=format",
  "tai-chi":
    "https://images.unsplash.com/photo-1560253414-d6535ae78f2c?w=500&auto=format",

  // Aktivitas Rekreasi (Recreational Activities)
  hiking:
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  mendaki:
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  "hiking trail":
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  "jalur pendakian":
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  "berjalan kaki":
    "https://images.unsplash.com/photo-1487956382158-bb926046304a?w=500&auto=format",
  trekking:
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  hiking:
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  basket:
    "https://images.unsplash.com/photo-1546519638-68e109acd27d?w=500&auto=format",
  basketball:
    "https://images.unsplash.com/photo-1546519638-68e109acd27d?w=500&auto=format",
  "bola basket":
    "https://images.unsplash.com/photo-1546519638-68e109acd27d?w=500&auto=format",
  "bermain basket":
    "https://images.unsplash.com/photo-1546519638-68e109acd27d?w=500&auto=format",
  badminton:
    "https://images.unsplash.com/photo-1626224583764-f87db24ac1e9?w=500&auto=format",
  "bermain badminton":
    "https://images.unsplash.com/photo-1626224583764-f87db24ac1e9?w=500&auto=format",
  bulutangkis:
    "https://images.unsplash.com/photo-1626224583764-f87db24ac1e9?w=500&auto=format",
  "tenis meja":
    "https://images.unsplash.com/photo-1534158914592-062992fbe900?w=500&auto=format",
  "table tennis":
    "https://images.unsplash.com/photo-1534158914592-062992fbe900?w=500&auto=format",
  "ping pong":
    "https://images.unsplash.com/photo-1534158914592-062992fbe900?w=500&auto=format",
  pingpong:
    "https://images.unsplash.com/photo-1534158914592-062992fbe900?w=500&auto=format",
  "sepak bola":
    "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=500&auto=format",
  soccer:
    "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=500&auto=format",
  football:
    "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=500&auto=format",
  futsal:
    "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=500&auto=format",
  voli: "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=500&auto=format",
  volleyball:
    "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=500&auto=format",
  "bola voli":
    "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=500&auto=format",
  tenis:
    "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=500&auto=format",
  tennis:
    "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=500&auto=format",
  "bermain tenis":
    "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=500&auto=format",
  "berenang santai":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "recreational swimming":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  "leisure swimming":
    "https://images.unsplash.com/photo-1600965962361-9035a2b404f5?w=500&auto=format",
  golf: "https://images.unsplash.com/photo-1580239556629-5a8456ec9b50?w=500&auto=format",
  "bermain golf":
    "https://images.unsplash.com/photo-1580239556629-5a8456ec9b50?w=500&auto=format",
  memancing:
    "https://images.unsplash.com/photo-1542396601-1dca79150918?w=500&auto=format",
  fishing:
    "https://images.unsplash.com/photo-1542396601-1dca79150918?w=500&auto=format",
  pancing:
    "https://images.unsplash.com/photo-1542396601-1dca79150918?w=500&auto=format",
  surfing:
    "https://images.unsplash.com/photo-1505459668311-8dfac7952bf0?w=500&auto=format",
  berselancar:
    "https://images.unsplash.com/photo-1505459668311-8dfac7952bf0?w=500&auto=format",
  selancar:
    "https://images.unsplash.com/photo-1505459668311-8dfac7952bf0?w=500&auto=format",
  climbing:
    "https://images.unsplash.com/photo-1578116922645-3976907a7671?w=500&auto=format",
  "rock climbing":
    "https://images.unsplash.com/photo-1578116922645-3976907a7671?w=500&auto=format",
  "panjat tebing":
    "https://images.unsplash.com/photo-1578116922645-3976907a7671?w=500&auto=format",
  "ice skating":
    "https://images.unsplash.com/photo-1548878460-82aaf9fd103d?w=500&auto=format",
  skating:
    "https://images.unsplash.com/photo-1548878460-82aaf9fd103d?w=500&auto=format",
  "seluncur es":
    "https://images.unsplash.com/photo-1548878460-82aaf9fd103d?w=500&auto=format",
  "roller skating":
    "https://images.unsplash.com/photo-1606592641978-bbaf912ebe2c?w=500&auto=format",
  "in-line skating":
    "https://images.unsplash.com/photo-1606592641978-bbaf912ebe2c?w=500&auto=format",
  "seluncur roda":
    "https://images.unsplash.com/photo-1606592641978-bbaf912ebe2c?w=500&auto=format",
  berkuda:
    "https://images.unsplash.com/photo-1571751239008-523927ca3abb?w=500&auto=format",
  horseback:
    "https://images.unsplash.com/photo-1571751239008-523927ca3abb?w=500&auto=format",
  "horse riding":
    "https://images.unsplash.com/photo-1571751239008-523927ca3abb?w=500&auto=format",
  menari:
    "https://images.unsplash.com/photo-1504609813442-a9924e2e4531?w=500&auto=format",
  dancing:
    "https://images.unsplash.com/photo-1504609813442-a9924e2e4531?w=500&auto=format",
  dance:
    "https://images.unsplash.com/photo-1504609813442-a9924e2e4531?w=500&auto=format",
  zumba:
    "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format",
  "dansa zumba":
    "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format",
  bowling:
    "https://images.unsplash.com/photo-1622623210795-ab34e2c88c53?w=500&auto=format",
  boling:
    "https://images.unsplash.com/photo-1622623210795-ab34e2c88c53?w=500&auto=format",
  "bermain bowling":
    "https://images.unsplash.com/photo-1622623210795-ab34e2c88c53?w=500&auto=format",
  kayaking:
    "https://images.unsplash.com/photo-1604537581227-6ae2dac87d48?w=500&auto=format",
  kayak:
    "https://images.unsplash.com/photo-1604537581227-6ae2dac87d48?w=500&auto=format",
  berkayak:
    "https://images.unsplash.com/photo-1604537581227-6ae2dac87d48?w=500&auto=format",
  rafting:
    "https://images.unsplash.com/photo-1561022821-b2bb202bf316?w=500&auto=format",
  "white water rafting":
    "https://images.unsplash.com/photo-1561022821-b2bb202bf316?w=500&auto=format",
  "arung jeram":
    "https://images.unsplash.com/photo-1561022821-b2bb202bf316?w=500&auto=format",
  snorkeling:
    "https://images.unsplash.com/photo-1586422689955-b4b036a8f214?w=500&auto=format",
  snorkel:
    "https://images.unsplash.com/photo-1586422689955-b4b036a8f214?w=500&auto=format",
  menyelam:
    "https://images.unsplash.com/photo-1586422689955-b4b036a8f214?w=500&auto=format",

  // Aktivitas Rumah (Home Activities)
  berkebun:
    "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=500&auto=format",
  gardening:
    "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=500&auto=format",
  kebun:
    "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=500&auto=format",
  memasak:
    "https://images.unsplash.com/photo-1507048331197-7d4ac70811cf?w=500&auto=format",
  cooking:
    "https://images.unsplash.com/photo-1507048331197-7d4ac70811cf?w=500&auto=format",
  masak:
    "https://images.unsplash.com/photo-1507048331197-7d4ac70811cf?w=500&auto=format",
  "membersihkan rumah":
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  cleaning:
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  menyapu:
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  mengepel:
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  vacuuming:
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  "pekerjaan rumah":
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  housework:
    "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format",
  mencuci:
    "https://images.unsplash.com/photo-1606513091518-5f0b91b1fa8a?w=500&auto=format",
  laundry:
    "https://images.unsplash.com/photo-1606513091518-5f0b91b1fa8a?w=500&auto=format",
  "membersihkan halaman":
    "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=500&auto=format",
  "yard work":
    "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=500&auto=format",
  DIY: "https://images.unsplash.com/photo-1550963295-019d8a8a61c5?w=500&auto=format",
  "do it yourself":
    "https://images.unsplash.com/photo-1550963295-019d8a8a61c5?w=500&auto=format",
  "home improvement":
    "https://images.unsplash.com/photo-1550963295-019d8a8a61c5?w=500&auto=format",
  "perbaikan rumah":
    "https://images.unsplash.com/photo-1550963295-019d8a8a61c5?w=500&auto=format",
};

// Placeholder default untuk gambar yang tidak ditemukan
const DEFAULT_ACTIVITY_IMAGE = {
  Cardio:
    "https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=500&auto=format",
  Strength:
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500&auto=format",
  Flexibility:
    "https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=500&auto=format",
  Recreation:
    "https://images.unsplash.com/photo-1551632811-561732d1e306?w=500&auto=format",
  Home: "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=500&auto=format",
  default:
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500&auto=format",
};

/**
 * Fungsi untuk mendapatkan gambar aktivitas berdasarkan nama
 * @param {string} activityName - Nama aktivitas
 * @param {string} activityType - Tipe aktivitas (optional)
 * @returns {string} URL gambar aktivitas
 */
export const getActivityImage = (activityName, activityType = "default") => {
  // Jika tidak ada nama aktivitas, gunakan gambar default berdasarkan tipe
  if (!activityName) {
    return (
      DEFAULT_ACTIVITY_IMAGE[activityType] || DEFAULT_ACTIVITY_IMAGE.default
    );
  }

  // Ubah ke lowercase untuk pencocokan yang lebih baik
  const activityNameLower = activityName.toLowerCase();

  // Pecah nama aktivitas menjadi kata-kata individual
  const words = activityNameLower.split(/\s+|[+]|\dengan|\dan/);

  // Cari kata kunci yang cocok dalam database gambar
  for (const keyword of Object.keys(activityImageDatabase)) {
    // Cek apakah ada kata dalam nama aktivitas yang cocok dengan keyword
    for (const word of words) {
      if (word.length > 2 && keyword.toLowerCase().includes(word)) {
        return activityImageDatabase[keyword];
      }
    }
  }

  // Cek jika aktivitas mengandung keyword yang ada di database
  for (const keyword of Object.keys(activityImageDatabase)) {
    if (activityNameLower.includes(keyword.toLowerCase())) {
      return activityImageDatabase[keyword];
    }
  }

  // Jika tidak ditemukan, coba cocokkan berdasarkan kategori aktivitas
  if (
    activityNameLower.includes("lari") ||
    activityNameLower.includes("jogging") ||
    activityNameLower.includes("jalan") ||
    activityNameLower.includes("sepeda") ||
    activityNameLower.includes("renang")
  ) {
    return DEFAULT_ACTIVITY_IMAGE.Cardio;
  } else if (
    activityNameLower.includes("angkat") ||
    activityNameLower.includes("push") ||
    activityNameLower.includes("press") ||
    activityNameLower.includes("beban") ||
    activityNameLower.includes("kekuatan")
  ) {
    return DEFAULT_ACTIVITY_IMAGE.Strength;
  } else if (
    activityNameLower.includes("yoga") ||
    activityNameLower.includes("stretching") ||
    activityNameLower.includes("peregangan")
  ) {
    return DEFAULT_ACTIVITY_IMAGE.Flexibility;
  } else if (
    activityNameLower.includes("kebun") ||
    activityNameLower.includes("masak") ||
    activityNameLower.includes("bersih")
  ) {
    return DEFAULT_ACTIVITY_IMAGE.Home;
  }

  // Jika tidak ditemukan sama sekali, gunakan gambar default
  return DEFAULT_ACTIVITY_IMAGE[activityType] || DEFAULT_ACTIVITY_IMAGE.default;
};

/**
 * Fungsi untuk memeriksa ketersediaan gambar
 * @param {string} url - URL gambar
 * @returns {boolean} true jika gambar tersedia, false jika tidak
 */
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

/**
 * Fungsi untuk mendapatkan emoji berdasarkan nama aktivitas
 * @param {string} activityName - Nama aktivitas
 * @returns {string} emoji yang sesuai
 */
export const getActivityEmoji = (activityName) => {
  if (!activityName) return "💪";

  const activityNameLower = activityName.toLowerCase();

  if (
    activityNameLower.includes("lari") ||
    activityNameLower.includes("jogging") ||
    activityNameLower.includes("run")
  ) {
    return "🏃‍♂️";
  } else if (
    activityNameLower.includes("sepeda") ||
    activityNameLower.includes("cycling") ||
    activityNameLower.includes("bike")
  ) {
    return "🚴‍♂️";
  } else if (
    activityNameLower.includes("renang") ||
    activityNameLower.includes("swim")
  ) {
    return "🏊‍♂️";
  } else if (
    activityNameLower.includes("jalan") ||
    activityNameLower.includes("walk")
  ) {
    return "🚶‍♂️";
  } else if (activityNameLower.includes("yoga")) {
    return "🧘‍♀️";
  } else if (
    activityNameLower.includes("beban") ||
    activityNameLower.includes("gym") ||
    activityNameLower.includes("weight")
  ) {
    return "🏋️‍♂️";
  } else if (
    activityNameLower.includes("basket") ||
    activityNameLower.includes("basketball")
  ) {
    return "🏀";
  } else if (
    activityNameLower.includes("bola") ||
    activityNameLower.includes("soccer") ||
    activityNameLower.includes("football")
  ) {
    return "⚽";
  } else if (
    activityNameLower.includes("tenis") ||
    activityNameLower.includes("tennis")
  ) {
    return "🎾";
  } else if (activityNameLower.includes("golf")) {
    return "⛳";
  } else if (activityNameLower.includes("badminton")) {
    return "🏸";
  } else if (
    activityNameLower.includes("ping") ||
    activityNameLower.includes("tenis meja")
  ) {
    return "🏓";
  } else if (
    activityNameLower.includes("masak") ||
    activityNameLower.includes("cook")
  ) {
    return "👨‍🍳";
  } else if (
    activityNameLower.includes("kebun") ||
    activityNameLower.includes("garden")
  ) {
    return "🌱";
  } else if (
    activityNameLower.includes("bersih") ||
    activityNameLower.includes("clean")
  ) {
    return "🧹";
  }

  return "💪";
};

export default {
  getActivityImage,
  checkImageAvailability,
  getActivityEmoji,
};
