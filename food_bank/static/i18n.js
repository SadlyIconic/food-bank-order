/**
 * Food bank i18n — English, Español, 中文, Tiếng Việt, Tagalog, Soomaali
 * (Seattle-area languages common among food bank clients)
 */
const FoodBankI18n = (() => {
  const LANG_KEY = "food_bank_lang";

  const LANGS = [
    { code: "en", native: "English", flag: "🇺🇸" },
    { code: "es", native: "Español", flag: "🇪🇸" },
    { code: "zh", native: "中文", flag: "🇨🇳" },
    { code: "vi", native: "Tiếng Việt", flag: "🇻🇳" },
    { code: "tl", native: "Tagalog", flag: "🇵🇭" },
    { code: "so", native: "Soomaali", flag: "🇸🇴" },
  ];

  const UI = {
    en: {
      app_name: "Food Bank Order",
      nav_shop: "Shop",
      nav_cart: "Cart",
      nav_give: "Give",
      nav_give_needs: "Needs board",
      nav_give_pledge: "Make a pledge",
      nav_back_ordering: "Back to ordering",
      nav_admin: "Admin",
      nav_request: "Share needs",
      request_title: "What do you need this week?",
      request_subtitle: "Tap a category to see what's included, then add the ones you expect to need.",
      request_week: "Week",
      request_submit: "Submit my needs",
      request_already_submitted: "You already shared your needs for this week. Thank you!",
      request_success_title: "Thank you!",
      request_success_body: "Your needs for this week have been recorded anonymously.",
      request_success_count: "Categories recorded:",
      request_success_back: "Back to board",
      request_info_aria: "Learn more about this category",
      request_modal_items: "Examples we often carry",
      request_modal_add: "Add to my needs",
      request_modal_remove: "Remove from my needs",
      request_modal_close: "Close",
      lang_label: "Language",
      shop_title: "Shop",
      shop_subtitle: "Browse items and add them to your cart ({limit} lb limit per order).",
      search: "Search",
      search_placeholder: "Search by name…",
      all: "All",
      per_unit: "per",
      add_to_cart: "Add to cart",
      added: "Added!",
      shop_empty: "No items match your search or filter.",
      clear_filters: "Clear filters",
      cart_title: "Your cart",
      cart_subtitle: "Review items before checkout ({weight}).",
      continue_shopping: "Continue shopping",
      review_order: "Review order",
      cart_empty: "Your cart is empty.",
      start_shopping: "Start shopping",
      confirm_title: "Confirm your order",
      confirm_subtitle: "Check everything looks right, then place your order.",
      back_to_cart: "Back to cart",
      place_order: "Place order",
      confirm_empty: "Nothing to confirm — your cart is empty.",
      go_to_shop: "Go to shop",
      qty: "Qty",
      quantity: "Quantity",
      remove: "Remove",
      requested: "Requested",
      getting: "Getting",
      shortfall: "Shortfall",
      weight_over_msg: "This would put you over the {limit} lb limit. Remove items or choose something lighter.",
      weight_over_cart: "Cart is {weight} lb — over the {limit} lb limit.",
      lb: "lb",
      decrease: "Decrease quantity",
      increase: "Increase quantity",
      item_col: "Item",
      community_app_name: "Neighborhood Give",
      community_nav_board: "Today's shortages",
      community_nav_pledge: "Pledge",
      community_needs_title: "Today's shortages",
      community_needs_subtitle: "Help your neighborhood food agency fill high-demand items. No login required.",
      community_pickup: "Pickup",
      community_not_recorded: "Today's shortages haven't been posted yet. Check back soon.",
      community_unpublished: "The neighborhood board is being prepared. Check back soon.",
      community_title: "Today's shortages",
      community_subtitle: "Help your neighborhood food agency fill high-demand items. No account needed.",
      community_not_ready: "Today's shortages haven't been posted yet. Check back soon.",
      community_not_published: "The shortage board is not live yet. Check back soon.",
      community_all_covered: "All shortages are covered today. Thank you!",
      community_pledge_btn: "Make a pledge",
      community_make_pledge: "Make a pledge",
      community_open_needs: "Open shortages",
      community_requested: "Requested",
      community_needed: "Needed",
      community_pledged: "Pledged",
      community_still_open: "Still open",
      community_high_demand: "High demand",
      community_legend_pledged: "Pledged",
      community_legend_open: "Still open",
      community_thanks_title: "Neighborhood thanks",
      community_thanks_body: "Donors who pledged today:",
      community_pledge_board: "Pledge board",
      community_pledge_board_sub: "Thank you to everyone contributing today.",
      community_donor: "Donor",
      community_donor_name: "Your name",
      community_note: "Note",
      household_optional: "(optional)",
      community_no_open_items: "Nothing open for pledges right now — thank you!",
      community_pledge_title: "Make a pledge",
      community_pledge_subtitle: "Help your neighborhood food agency by pledging items from today's shortage list.",
      community_back_board: "Back to shortages board",
      community_donor_placeholder: "e.g. Maria",
      community_anonymous: "Anonymous donor",
      community_note_placeholder: "e.g. I'll drop off Saturday morning",
      community_submit_pledge: "Submit pledge",
      community_pledge_status: "Status",
      community_status_pledged: "Pledged",
      community_status_received: "Received",
      community_remaining_hint: "Up to {count} still open for this item.",
      community_option_label: "{name} — {count} {unit} still open",
    },
    es: {
      app_name: "Pedido del Banco de Alimentos",
      nav_shop: "Tienda",
      nav_cart: "Carrito",
      nav_give: "Donar",
      nav_give_needs: "Escasez de hoy",
      nav_give_pledge: "Comprometerse",
      nav_back_ordering: "Volver al pedido",
      nav_admin: "Admin",
      lang_label: "Idioma",
      shop_title: "Tienda",
      shop_subtitle: "Explore artículos y agréguelos al carrito (límite de {limit} lb por pedido).",
      search: "Buscar",
      search_placeholder: "Buscar por nombre…",
      all: "Todos",
      per_unit: "por",
      add_to_cart: "Agregar al carrito",
      added: "¡Agregado!",
      shop_empty: "Ningún artículo coincide con su búsqueda.",
      clear_filters: "Borrar filtros",
      cart_title: "Su carrito",
      cart_subtitle: "Revise los artículos antes de pagar ({weight}).",
      continue_shopping: "Seguir comprando",
      review_order: "Revisar pedido",
      cart_empty: "Su carrito está vacío.",
      start_shopping: "Empezar a comprar",
      confirm_title: "Confirmar pedido",
      confirm_subtitle: "Verifique que todo esté correcto y luego confirme.",
      back_to_cart: "Volver al carrito",
      place_order: "Realizar pedido",
      confirm_empty: "Nada que confirmar — su carrito está vacío.",
      go_to_shop: "Ir a la tienda",
      qty: "Cant.",
      quantity: "Cantidad",
      remove: "Quitar",
      requested: "Solicitado",
      getting: "Recibirá",
      shortfall: "Faltante",
      weight_over_msg: "Esto superaría el límite de {limit} lb. Quite artículos o elija algo más ligero.",
      weight_over_cart: "El carrito pesa {weight} lb — supera el límite de {limit} lb.",
      lb: "lb",
      decrease: "Disminuir cantidad",
      increase: "Aumentar cantidad",
      item_col: "Artículo",
      community_app_name: "Vecindario — Donar",
      community_nav_board: "Escasez de hoy",
      community_nav_pledge: "Comprometerse",
      community_needs_title: "Escasez de hoy",
      community_needs_subtitle: "Ayude a su agencia de alimentos del vecindario. No necesita cuenta.",
      community_not_recorded: "Las escaseces de hoy aún no se han publicado. Vuelva pronto.",
      community_unpublished: "El tablero del vecindario se está preparando. Vuelva pronto.",
      community_all_covered: "Todas las escaseces están cubiertas hoy. ¡Gracias!",
      community_open_needs: "Escasez abierta",
      community_requested: "Solicitado",
      community_pledged: "Comprometido",
      community_still_open: "Aún abierto",
      community_high_demand: "Alta demanda",
      community_thanks_title: "Gracias del vecindario",
      community_thanks_body: "Donantes que se comprometieron hoy:",
      community_pledge_board: "Compromisos",
      community_donor: "Donante",
      community_note: "Nota",
      household_optional: "(opcional)",
      community_no_open_items: "Nada abierto para compromisos ahora — ¡gracias!",
      community_pledge_title: "Hacer un compromiso",
      community_pledge_subtitle: "Ayude a su agencia comprometiéndose con artículos de la lista de escasez de hoy.",
      community_back_board: "Volver al tablero de escasez",
      community_donor_placeholder: "ej. María",
      community_anonymous: "Donante anónimo",
      community_note_placeholder: "ej. Lo dejaré el sábado por la mañana",
      community_submit_pledge: "Enviar compromiso",
      community_pledge_status: "Estado",
      community_status_pledged: "Comprometido",
      community_status_received: "Recibido",
      community_remaining_hint: "Aún faltan hasta {count} para este artículo.",
      community_option_label: "{name} — faltan {count} {unit}",
    },
    zh: {
      app_name: "食物银行订购",
      nav_shop: "选购",
      nav_cart: "购物车",
      nav_give: "捐赠",
      nav_give_needs: "今日短缺",
      nav_give_pledge: "承诺捐赠",
      nav_back_ordering: "返回订购",
      nav_admin: "管理",
      lang_label: "语言",
      shop_title: "选购",
      shop_subtitle: "浏览物品并加入购物车（每单限重 {limit} 磅）。",
      search: "搜索",
      search_placeholder: "按名称搜索…",
      all: "全部",
      per_unit: "每",
      add_to_cart: "加入购物车",
      added: "已添加！",
      shop_empty: "没有符合搜索条件的物品。",
      clear_filters: "清除筛选",
      cart_title: "您的购物车",
      cart_subtitle: "结账前请核对物品（{weight}）。",
      continue_shopping: "继续选购",
      review_order: "核对订单",
      cart_empty: "购物车是空的。",
      start_shopping: "开始选购",
      confirm_title: "确认订单",
      confirm_subtitle: "请确认无误后提交订单。",
      back_to_cart: "返回购物车",
      place_order: "提交订单",
      confirm_empty: "无需确认 — 购物车是空的。",
      go_to_shop: "去选购",
      qty: "数量",
      quantity: "数量",
      remove: "移除",
      requested: "申请",
      getting: "可获得",
      shortfall: "短缺",
      weight_over_msg: "这将超过 {limit} 磅限制。请移除物品或选择更轻的。",
      weight_over_cart: "购物车 {weight} 磅 — 超过 {limit} 磅限制。",
      lb: "磅",
      decrease: "减少数量",
      increase: "增加数量",
      item_col: "物品",
      community_app_name: "社区捐赠",
      community_nav_board: "今日短缺",
      community_nav_pledge: "承诺捐赠",
      community_needs_title: "今日短缺",
      community_needs_subtitle: "帮助您社区的食物机构填补高需求物品。无需登录。",
      community_not_recorded: "今日短缺尚未发布。请稍后再来。",
      community_unpublished: "社区捐赠板正在准备中。请稍后再来。",
      community_all_covered: "今日所有短缺已满足。谢谢！",
      community_open_needs: "开放短缺",
      community_requested: "申请",
      community_pledged: "已承诺",
      community_still_open: "仍缺",
      community_high_demand: "高需求",
      community_thanks_title: "社区感谢",
      community_thanks_body: "今日承诺捐赠的人：",
      community_pledge_board: "捐赠承诺",
      community_donor: "捐赠者",
      community_note: "备注",
      household_optional: "（可选）",
      community_no_open_items: "目前没有开放承诺 — 谢谢！",
      community_pledge_title: "承诺捐赠",
      community_pledge_subtitle: "通过承诺今日短缺清单上的物品来帮助社区食物机构。",
      community_back_board: "返回短缺板",
      community_donor_placeholder: "例如：张",
      community_anonymous: "匿名捐赠",
      community_note_placeholder: "例如：周六上午送达",
      community_submit_pledge: "提交承诺",
      community_pledge_status: "状态",
      community_status_pledged: "已承诺",
      community_status_received: "已收到",
      community_remaining_hint: "此物品仍缺最多 {count}。",
      community_option_label: "{name} — 仍缺 {count} {unit}",
    },
    vi: {
      app_name: "Đặt hàng Ngân hàng Thực phẩm",
      nav_shop: "Mua sắm",
      nav_cart: "Giỏ hàng",
      nav_give: "Quyên góp",
      nav_give_needs: "Thiếu hụt hôm nay",
      nav_give_pledge: "Cam kết",
      nav_back_ordering: "Quay lại đặt hàng",
      nav_admin: "Quản trị",
      lang_label: "Ngôn ngữ",
      shop_title: "Mua sắm",
      shop_subtitle: "Xem sản phẩm và thêm vào giỏ (giới hạn {limit} lb mỗi đơn).",
      search: "Tìm kiếm",
      search_placeholder: "Tìm theo tên…",
      all: "Tất cả",
      per_unit: "mỗi",
      add_to_cart: "Thêm vào giỏ",
      added: "Đã thêm!",
      shop_empty: "Không có sản phẩm phù hợp.",
      clear_filters: "Xóa bộ lọc",
      cart_title: "Giỏ hàng của bạn",
      cart_subtitle: "Kiểm tra trước khi đặt hàng ({weight}).",
      continue_shopping: "Tiếp tục mua",
      review_order: "Xem lại đơn",
      cart_empty: "Giỏ hàng trống.",
      start_shopping: "Bắt đầu mua",
      confirm_title: "Xác nhận đơn hàng",
      confirm_subtitle: "Kiểm tra kỹ rồi đặt hàng.",
      back_to_cart: "Quay lại giỏ",
      place_order: "Đặt hàng",
      confirm_empty: "Không có gì để xác nhận — giỏ trống.",
      go_to_shop: "Đi mua sắm",
      qty: "SL",
      quantity: "Số lượng",
      remove: "Xóa",
      requested: "Yêu cầu",
      getting: "Nhận được",
      shortfall: "Thiếu",
      weight_over_msg: "Vượt quá giới hạn {limit} lb. Hãy bỏ bớt hoặc chọn món nhẹ hơn.",
      weight_over_cart: "Giỏ {weight} lb — vượt giới hạn {limit} lb.",
      lb: "lb",
      decrease: "Giảm số lượng",
      increase: "Tăng số lượng",
      item_col: "Mặt hàng",
      community_app_name: "Cộng đồng — Quyên góp",
      community_nav_board: "Thiếu hụt hôm nay",
      community_nav_pledge: "Cam kết",
      community_needs_title: "Thiếu hụt hôm nay",
      community_needs_subtitle: "Giúp cơ quan thực phẩm khu phố lấp đầy mặt hàng nhu cầu cao. Không cần đăng nhập.",
      community_not_recorded: "Thiếu hụt hôm nay chưa được đăng. Hãy quay lại sau.",
      community_unpublished: "Bảng khu phố đang được chuẩn bị. Hãy quay lại sau.",
      community_all_covered: "Mọi thiếu hụt hôm nay đã được đáp ứng. Cảm ơn!",
      community_open_needs: "Thiếu hụt còn mở",
      community_requested: "Yêu cầu",
      community_pledged: "Đã cam kết",
      community_still_open: "Còn thiếu",
      community_high_demand: "Nhu cầu cao",
      community_thanks_title: "Cảm ơn khu phố",
      community_thanks_body: "Người quyên góp đã cam kết hôm nay:",
      community_pledge_board: "Cam kết cộng đồng",
      community_donor: "Người quyên góp",
      community_note: "Ghi chú",
      household_optional: "(tuỳ chọn)",
      community_no_open_items: "Không có gì mở để cam kết — cảm ơn!",
      community_pledge_title: "Cam kết quyên góp",
      community_pledge_subtitle: "Giúp cơ quan thực phẩm bằng cách cam kết mặt hàng từ danh sách thiếu hụt hôm nay.",
      community_back_board: "Quay lại bảng thiếu hụt",
      community_donor_placeholder: "vd. Lan",
      community_anonymous: "Ẩn danh",
      community_note_placeholder: "vd. Tôi sẽ giao sáng thứ Bảy",
      community_submit_pledge: "Gửi cam kết",
      community_pledge_status: "Trạng thái",
      community_status_pledged: "Đã cam kết",
      community_status_received: "Đã nhận",
      community_remaining_hint: "Còn thiếu tối đa {count} cho mặt hàng này.",
      community_option_label: "{name} — còn thiếu {count} {unit}",
    },
    tl: {
      app_name: "Order sa Food Bank",
      nav_shop: "Mamili",
      nav_cart: "Cart",
      nav_give: "Magbigay",
      nav_give_needs: "Kulang ngayon",
      nav_give_pledge: "Mag-pledge",
      nav_back_ordering: "Bumalik sa order",
      nav_admin: "Admin",
      lang_label: "Wika",
      shop_title: "Mamili",
      shop_subtitle: "Tingnan ang mga item at idagdag sa cart ({limit} lb limit bawat order).",
      search: "Maghanap",
      search_placeholder: "Hanapin ayon sa pangalan…",
      all: "Lahat",
      per_unit: "bawat",
      add_to_cart: "Idagdag sa cart",
      added: "Naidagdag!",
      shop_empty: "Walang item na tumugma sa paghahanap.",
      clear_filters: "I-clear ang filter",
      cart_title: "Iyong cart",
      cart_subtitle: "Suriin bago mag-checkout ({weight}).",
      continue_shopping: "Magpatuloy mamili",
      review_order: "Suriin ang order",
      cart_empty: "Walang laman ang cart.",
      start_shopping: "Magsimulang mamili",
      confirm_title: "Kumpirmahin ang order",
      confirm_subtitle: "Siguraduhing tama ang lahat bago mag-order.",
      back_to_cart: "Bumalik sa cart",
      place_order: "Mag-order",
      confirm_empty: "Walang ikukumpirma — walang laman ang cart.",
      go_to_shop: "Pumunta sa tindahan",
      qty: "Dami",
      quantity: "Dami",
      remove: "Alisin",
      requested: "Hiniling",
      getting: "Makakakuha",
      shortfall: "Kulang",
      weight_over_msg: "Lalampas sa {limit} lb limit. Mag-alis ng item o pumili ng mas magaan.",
      weight_over_cart: "Ang cart ay {weight} lb — lampas sa {limit} lb limit.",
      lb: "lb",
      decrease: "Bawasan ang dami",
      increase: "Dagdagan ang dami",
      item_col: "Item",
      community_app_name: "Kapitbahayan — Magbigay",
      community_nav_board: "Kulang ngayon",
      community_nav_pledge: "Mag-pledge",
      community_needs_title: "Kulang ngayon",
      community_needs_subtitle: "Tumulong sa inyong food agency sa kapitbahayan. Walang login na kailangan.",
      community_not_recorded: "Hindi pa nai-post ang kulang ngayon. Bumalik muli.",
      community_unpublished: "Inihahanda pa ang board ng kapitbahayan. Bumalik muli.",
      community_all_covered: "Lahat ng kulang ngayon ay natugunan. Salamat!",
      community_open_needs: "Bukas na kulang",
      community_requested: "Hiniling",
      community_pledged: "Na-pledge",
      community_still_open: "Bukas pa",
      community_high_demand: "Mataas na demand",
      community_thanks_title: "Pasasalamat ng kapitbahayan",
      community_thanks_body: "Mga donor na nag-pledge ngayon:",
      community_pledge_board: "Mga pledge",
      community_donor: "Donor",
      community_note: "Tala",
      household_optional: "(opsyonal)",
      community_no_open_items: "Walang bukas para sa pledge — salamat!",
      community_pledge_title: "Mag-pledge",
      community_pledge_subtitle: "Tumulong sa food agency sa pamamagitan ng pag-pledge mula sa listahan ng kulang ngayon.",
      community_back_board: "Bumalik sa shortages board",
      community_donor_placeholder: "hal. Maria",
      community_anonymous: "Anonymous na donor",
      community_note_placeholder: "hal. Idedrop off ko Sabado ng umaga",
      community_submit_pledge: "Isumite ang pledge",
      community_pledge_status: "Status",
      community_status_pledged: "Na-pledge",
      community_status_received: "Natanggap",
      community_remaining_hint: "Hanggang {count} pa ang bukas para sa item na ito.",
      community_option_label: "{name} — {count} {unit} pa ang bukas",
    },
    so: {
      app_name: "Dalabka Bangiga Cuntada",
      nav_shop: "Iibso",
      nav_cart: "Gaariga",
      nav_give: "Bixi",
      nav_give_needs: "Yaraanta maanta",
      nav_give_pledge: "Ballanqaad",
      nav_back_ordering: "Ku noqo dalabka",
      nav_admin: "Maamul",
      lang_label: "Luqadda",
      shop_title: "Iibso",
      shop_subtitle: "Eeg alaabta oo ku dar gaariga (xadka {limit} lb dalab kasta).",
      search: "Raadi",
      search_placeholder: "Raadi magaca…",
      all: "Dhammaan",
      per_unit: "halkii",
      add_to_cart: "Ku dar gaariga",
      added: "Waa lagu daray!",
      shop_empty: "Ma jiraan alaab ku habboon raadintaada.",
      clear_filters: "Nadiifi shaandhada",
      cart_title: "Gaarigaaga",
      cart_subtitle: "Hubi ka hor intaadan dalban ({weight}).",
      continue_shopping: "Sii wad iibsiga",
      review_order: "Hubi dalabka",
      cart_empty: "Gaarigu waa madhan yahay.",
      start_shopping: "Bilow iibsiga",
      confirm_title: "Xaqiiji dalabka",
      confirm_subtitle: "Hubi in wax walba sax yihiin ka dibna dalbo.",
      back_to_cart: "Ku noqo gaariga",
      place_order: "Dalbo",
      confirm_empty: "Wax xaqiijin ah ma jiro — gaarigu waa madhan.",
      go_to_shop: "Tag dukaanka",
      qty: "Tirada",
      quantity: "Tirada",
      remove: "Ka saar",
      requested: "La codsaday",
      getting: "Helitaanka",
      shortfall: "Yaraanta",
      weight_over_msg: "Tani waxay dhaafi doontaa xadka {limit} lb. Ka saar alaab ama dooro mid fudud.",
      weight_over_cart: "Gaarigu waa {weight} lb — wuu dhaafay xadka {limit} lb.",
      lb: "lb",
      decrease: "Yaree tirada",
      increase: "Kordhi tirada",
      item_col: "Alaab",
      community_app_name: "Bulshada — Bixi",
      community_nav_board: "Yaraanta maanta",
      community_nav_pledge: "Ballanqaad",
      community_needs_title: "Yaraanta maanta",
      community_needs_subtitle: "Ka caawi wakaaladda cuntada ee xaafaddaada. Akoon looma baahna.",
      community_not_recorded: "Yaraanta maanta weli lama daabicin. Soo noqo dhowaan.",
      community_unpublished: "Guddiga xaafadda waa la diyaarinayaa. Soo noqo dhowaan.",
      community_all_covered: "Dhammaan yaraanta maanta waa la daboolay. Mahadsanid!",
      community_open_needs: "Yaraanta furan",
      community_requested: "La codsaday",
      community_pledged: "La ballanqaaday",
      community_still_open: "Wali furan",
      community_high_demand: "Baahida sare",
      community_thanks_title: "Mahadsanid xaafadda",
      community_thanks_body: "Bixiyeyaasha ballanqaaday maanta:",
      community_pledge_board: "Ballanqaadyada",
      community_donor: "Bixiye",
      community_note: "Qoraal",
      household_optional: "(ikhtiyaari)",
      community_no_open_items: "Wax furan oo ballanqaad ah ma jiro — mahadsanid!",
      community_pledge_title: "Ballanqaad bixin",
      community_pledge_subtitle: "Ka caawi wakaaladda adigoo ballanqaadaya alaab ka mid ah liiska yaraanta maanta.",
      community_back_board: "Ku noqo guddiga yaraanta",
      community_donor_placeholder: "tusaale Amina",
      community_anonymous: "Bixiye qarsoodi ah",
      community_note_placeholder: "tusaale Sabtida subaxdii waan keeni doonaa",
      community_submit_pledge: "Gudbi ballanqaadka",
      community_pledge_status: "Xaaladda",
      community_status_pledged: "La ballanqaaday",
      community_status_received: "La helay",
      community_remaining_hint: "Ilaa {count} ayaa weli furan alaabtan.",
      community_option_label: "{name} — {count} {unit} ayaa weli furan",
    },
  };

  const CATEGORIES = {
    en: { Produce: "Produce", Protein: "Protein", Dairy: "Dairy", Grains: "Grains", "Canned Goods": "Canned Goods", Snacks: "Snacks", Beverages: "Beverages", Frozen: "Frozen", Household: "Household" },
    es: { Produce: "Productos frescos", Protein: "Proteína", Dairy: "Lácteos", Grains: "Granos", "Canned Goods": "Enlatados", Snacks: "Snacks", Beverages: "Bebidas", Frozen: "Congelados", Household: "Hogar" },
    zh: { Produce: "农产品", Protein: "蛋白质", Dairy: "乳制品", Grains: "谷物", "Canned Goods": "罐头", Snacks: "零食", Beverages: "饮料", Frozen: "冷冻", Household: "日用品" },
    vi: { Produce: "Rau củ quả", Protein: "Protein", Dairy: "Sữa", Grains: "Ngũ cốc", "Canned Goods": "Đồ hộp", Snacks: "Đồ ăn vặt", Beverages: "Đồ uống", Frozen: "Đông lạnh", Household: "Gia dụng" },
    tl: { Produce: "Gulay at prutas", Protein: "Protina", Dairy: "Gatas", Grains: "Butil", "Canned Goods": "De-lata", Snacks: "Meryenda", Beverages: "Inumin", Frozen: "Frozen", Household: "Pangbahay" },
    so: { Produce: "Khudaarta", Protein: "Borotiin", Dairy: "Caano", Grains: "Badar", "Canned Goods": "Qasacadaysan", Snacks: "Cunto fudud", Beverages: "Cabbitaan", Frozen: "Barafaysan", Household: "Guriga" },
  };

  const UNITS = {
    en: { lb: "lb", bunch: "bunch", head: "head", dozen: "dozen", jar: "jar", can: "can", bag: "bag", pack: "pack", gallon: "gallon", tub: "tub", box: "box", loaf: "loaf", canister: "canister", bottle: "bottle", pizza: "pizza", tube: "tube" },
    es: { lb: "lb", bunch: "manojo", head: "cabeza", dozen: "docena", jar: "frasco", can: "lata", bag: "bolsa", pack: "paquete", gallon: "galón", tub: "envase", box: "caja", loaf: "pan", canister: "bote", bottle: "botella", pizza: "pizza", tube: "tubo" },
    zh: { lb: "磅", bunch: "把", head: "颗", dozen: "打", jar: "罐", can: "罐", bag: "袋", pack: "包", gallon: "加仑", tub: "桶", box: "盒", loaf: "条", canister: "筒", bottle: "瓶", pizza: "比萨", tube: "管" },
    vi: { lb: "lb", bunch: "bó", head: "cây", dozen: "tá", jar: "lọ", can: "lon", bag: "túi", pack: "gói", gallon: "gallon", tub: "hộp", box: "hộp", loaf: "ổ", canister: "bình", bottle: "chai", pizza: "pizza", tube: "tuýp" },
    tl: { lb: "lb", bunch: "bungkos", head: "ulo", dozen: "dosena", jar: "garapon", can: "lata", bag: "supot", pack: "pakete", gallon: "galon", tub: "lalagyan", box: "kahon", loaf: "tinapay", canister: "lata", bottle: "bote", pizza: "pizza", tube: "tube" },
    so: { lb: "lb", bunch: "dhar", head: "madax", dozen: "duqsin", jar: "dheri", can: "qasac", bag: "bac", pack: "xirmo", gallon: "gaalo", tub: "weel", box: "sanduuq", loaf: "rooti", canister: "weel", bottle: "dhalo", pizza: "pizza", tube: "tuubbo" },
  };

  const ITEMS = {
    en: { apples: "Apples", bananas: "Bananas", oranges: "Oranges", potatoes: "Potatoes", onions: "Yellow onions", carrots: "Carrots", celery: "Celery", lettuce: "Romaine lettuce", "tomatoes-fresh": "Fresh tomatoes", broccoli: "Broccoli", "chicken-breast": "Chicken breast", "ground-beef": "Ground beef", eggs: "Eggs (dozen)", "peanut-butter": "Peanut butter (16 oz)", tuna: "Canned tuna (5 oz)", "lentils-dry": "Dry lentils (1 lb bag)", "turkey-slices": "Deli turkey slices", milk: "Whole milk (gallon)", "cheese-shredded": "Shredded cheddar cheese", yogurt: "Plain yogurt (32 oz)", butter: "Butter (1 lb)", "cottage-cheese": "Cottage cheese (16 oz)", "rice-white": "White rice (2 lb bag)", "rice-brown": "Brown rice (2 lb bag)", "pasta-spaghetti": "Spaghetti (1 lb)", "pasta-macaroni": "Macaroni (1 lb)", "bread-loaf": "Whole wheat bread", oatmeal: "Oatmeal (42 oz)", flour: "All-purpose flour (5 lb)", cereal: "Breakfast cereal", "black-beans": "Black beans (15 oz can)", "kidney-beans": "Kidney beans (15 oz can)", "tomatoes-canned": "Diced tomatoes (14.5 oz can)", "tomato-sauce": "Tomato sauce (15 oz can)", "chicken-soup": "Chicken noodle soup", "vegetable-soup": "Vegetable soup", "corn-canned": "Canned corn", "green-beans-canned": "Canned green beans", crackers: "Saltine crackers", "granola-bars": "Granola bars (box of 8)", applesauce: "Applesauce cups (6-pack)", raisins: "Raisins (12 oz)", "juice-apple": "Apple juice (64 oz)", "juice-orange": "Orange juice (64 oz)", coffee: "Ground coffee (12 oz)", tea: "Tea bags (100 count)", "frozen-vegetables": "Frozen mixed vegetables", "frozen-fish": "Frozen fish fillets", "frozen-pizza": "Frozen cheese pizza", diapers: "Diapers (size 4, 28 count)", "soap-bar": "Bar soap (3-pack)", toothpaste: "Toothpaste", "toilet-paper": "Toilet paper (4 roll)", "laundry-detergent": "Laundry detergent" },
    es: { apples: "Manzanas", bananas: "Plátanos", oranges: "Naranjas", potatoes: "Papas", onions: "Cebollas amarillas", carrots: "Zanahorias", celery: "Apio", lettuce: "Lechuga romana", "tomatoes-fresh": "Tomates frescos", broccoli: "Brócoli", "chicken-breast": "Pechuga de pollo", "ground-beef": "Carne molida", eggs: "Huevos (docena)", "peanut-butter": "Mantequilla de maní (16 oz)", tuna: "Atún en lata (5 oz)", "lentils-dry": "Lentejas secas (1 lb)", "turkey-slices": "Pavo en rebanadas", milk: "Leche entera (galón)", "cheese-shredded": "Queso cheddar rallado", yogurt: "Yogur natural (32 oz)", butter: "Mantequilla (1 lb)", "cottage-cheese": "Requesón (16 oz)", "rice-white": "Arroz blanco (2 lb)", "rice-brown": "Arroz integral (2 lb)", "pasta-spaghetti": "Espagueti (1 lb)", "pasta-macaroni": "Macarrones (1 lb)", "bread-loaf": "Pan integral", oatmeal: "Avena (42 oz)", flour: "Harina (5 lb)", cereal: "Cereal de desayuno", "black-beans": "Frijoles negros (lata 15 oz)", "kidney-beans": "Frijoles rojos (lata 15 oz)", "tomatoes-canned": "Tomates en cubos (lata)", "tomato-sauce": "Salsa de tomate (lata)", "chicken-soup": "Sopa de pollo con fideos", "vegetable-soup": "Sopa de verduras", "corn-canned": "Maíz en lata", "green-beans-canned": "Ejotes en lata", crackers: "Galletas saladas", "granola-bars": "Barras de granola (8)", applesauce: "Compota de manzana (6)", raisins: "Pasas (12 oz)", "juice-apple": "Jugo de manzana (64 oz)", "juice-orange": "Jugo de naranja (64 oz)", coffee: "Café molido (12 oz)", tea: "Bolsitas de té (100)", "frozen-vegetables": "Verduras mixtas congeladas", "frozen-fish": "Filetes de pescado congelados", "frozen-pizza": "Pizza congelada", diapers: "Pañales (talla 4, 28)", "soap-bar": "Jabón en barra (3)", toothpaste: "Pasta dental", "toilet-paper": "Papel higiénico (4 rollos)", "laundry-detergent": "Detergente para ropa" },
    zh: { apples: "苹果", bananas: "香蕉", oranges: "橙子", potatoes: "土豆", onions: "黄洋葱", carrots: "胡萝卜", celery: "芹菜", lettuce: "罗马生菜", "tomatoes-fresh": "新鲜番茄", broccoli: "西兰花", "chicken-breast": "鸡胸肉", "ground-beef": "牛肉馅", eggs: "鸡蛋（一打）", "peanut-butter": "花生酱（16盎司）", tuna: "罐头金枪鱼（5盎司）", "lentils-dry": "干扁豆（1磅）", "turkey-slices": "火鸡切片", milk: "全脂牛奶（加仑）", "cheese-shredded": "切达奶酪丝", yogurt: "原味酸奶（32盎司）", butter: "黄油（1磅）", "cottage-cheese": "农家奶酪（16盎司）", "rice-white": "白米（2磅）", "rice-brown": "糙米（2磅）", "pasta-spaghetti": "意大利面（1磅）", "pasta-macaroni": "通心粉（1磅）", "bread-loaf": "全麦面包", oatmeal: "燕麦片（42盎司）", flour: "通用面粉（5磅）", cereal: "早餐麦片", "black-beans": "黑豆罐头（15盎司）", "kidney-beans": "芸豆罐头（15盎司）", "tomatoes-canned": "番茄丁罐头", "tomato-sauce": "番茄酱罐头", "chicken-soup": "鸡肉面汤", "vegetable-soup": "蔬菜汤", "corn-canned": "罐头玉米", "green-beans-canned": "罐头四季豆", crackers: "苏打饼干", "granola-bars": "麦片棒（8条）", applesauce: "苹果酱杯（6杯）", raisins: "葡萄干（12盎司）", "juice-apple": "苹果汁（64盎司）", "juice-orange": "橙汁（64盎司）", coffee: "咖啡粉（12盎司）", tea: "茶包（100包）", "frozen-vegetables": "冷冻杂蔬", "frozen-fish": "冷冻鱼片", "frozen-pizza": "冷冻芝士披萨", diapers: "尿布（4号，28片）", "soap-bar": "香皂（3块）", toothpaste: "牙膏", "toilet-paper": "卷纸（4卷）", "laundry-detergent": "洗衣液" },
    vi: { apples: "Táo", bananas: "Chuối", oranges: "Cam", potatoes: "Khoai tây", onions: "Hành vàng", carrots: "Cà rốt", celery: "Cần tây", lettuce: "Xà lách romaine", "tomatoes-fresh": "Cà chua tươi", broccoli: "Bông cải xanh", "chicken-breast": "Ức gà", "ground-beef": "Thịt bò xay", eggs: "Trứng (tá)", "peanut-butter": "Bơ đậu phộng (16 oz)", tuna: "Cá ngừ hộp (5 oz)", "lentils-dry": "Đậu lăng khô (1 lb)", "turkey-slices": "Gà tây lát", milk: "Sữa nguyên kem (gallon)", "cheese-shredded": "Phô mai cheddar bào", yogurt: "Sữa chua nguyên chất (32 oz)", butter: "Bơ (1 lb)", "cottage-cheese": "Phô mai cottage (16 oz)", "rice-white": "Gạo trắng (2 lb)", "rice-brown": "Gạo lứt (2 lb)", "pasta-spaghetti": "Mì spaghetti (1 lb)", "pasta-macaroni": "Nui (1 lb)", "bread-loaf": "Bánh mì nguyên cám", oatmeal: "Yến mạch (42 oz)", flour: "Bột mì (5 lb)", cereal: "Ngũ cốc ăn sáng", "black-beans": "Đậu đen hộp (15 oz)", "kidney-beans": "Đậu đỏ hộp (15 oz)", "tomatoes-canned": "Cà chua xắc hộp", "tomato-sauce": "Sốt cà chua hộp", "chicken-soup": "Súp mì gà", "vegetable-soup": "Súp rau", "corn-canned": "Ngô hộp", "green-beans-canned": "Đậu xanh hộp", crackers: "Bánh quy mặn", "granola-bars": "Thanh granola (8)", applesauce: "Sốt táo (6 hộp)", raisins: "Nho khô (12 oz)", "juice-apple": "Nước táo (64 oz)", "juice-orange": "Nước cam (64 oz)", coffee: "Cà phê xay (12 oz)", tea: "Trà túi (100)", "frozen-vegetables": "Rau củ đông lạnh", "frozen-fish": "Phi lê cá đông lạnh", "frozen-pizza": "Pizza đông lạnh", diapers: "Tã (size 4, 28)", "soap-bar": "Xà phòng (3)", toothpaste: "Kem đánh răng", "toilet-paper": "Giấy vệ sinh (4 cuộn)", "laundry-detergent": "Nước giặt" },
    tl: { apples: "Mansanas", bananas: "Saging", oranges: "Kahel", potatoes: "Patatas", onions: "Sibuyas", carrots: "Karot", celery: "Kintsay", lettuce: "Lettuce", "tomatoes-fresh": "Sariwang kamatis", broccoli: "Broccoli", "chicken-breast": "Dada ng manok", "ground-beef": "Giniling na baka", eggs: "Itlog (dosena)", "peanut-butter": "Peanut butter (16 oz)", tuna: "Tunang de-lata (5 oz)", "lentils-dry": "Tuyong lentils (1 lb)", "turkey-slices": "Hiwa ng pabo", milk: "Gatas (galon)", "cheese-shredded": "Kinud na cheddar", yogurt: "Plain yogurt (32 oz)", butter: "Mantekilya (1 lb)", "cottage-cheese": "Cottage cheese (16 oz)", "rice-white": "Puting bigas (2 lb)", "rice-brown": "Brown rice (2 lb)", "pasta-spaghetti": "Spaghetti (1 lb)", "pasta-macaroni": "Macaroni (1 lb)", "bread-loaf": "Whole wheat na tinapay", oatmeal: "Oatmeal (42 oz)", flour: "Harina (5 lb)", cereal: "Cereal sa almusal", "black-beans": "Itim na beans (de-lata)", "kidney-beans": "Kidney beans (de-lata)", "tomatoes-canned": "Kamatis na de-lata", "tomato-sauce": "Sarsa ng kamatis", "chicken-soup": "Chicken noodle soup", "vegetable-soup": "Gulay na soup", "corn-canned": "Mais na de-lata", "green-beans-canned": "Green beans de-lata", crackers: "Crackers", "granola-bars": "Granola bars (8)", applesauce: "Applesauce (6)", raisins: "Pasas (12 oz)", "juice-apple": "Apple juice (64 oz)", "juice-orange": "Orange juice (64 oz)", coffee: "Kape (12 oz)", tea: "Tsaa (100)", "frozen-vegetables": "Frozen na gulay", "frozen-fish": "Frozen na isda", "frozen-pizza": "Frozen pizza", diapers: "Lampin (size 4, 28)", "soap-bar": "Sabon (3)", toothpaste: "Toothpaste", "toilet-paper": "Toilet paper (4 roll)", "laundry-detergent": "Detergent sa damit" },
    so: { apples: "Tufaax", bananas: "Moos", oranges: "Liin", potatoes: "Baradho", onions: "Basal", carrots: "Karoot", celery: "Selari", lettuce: "Letis", "tomatoes-fresh": "Yaanyo cusub", broccoli: "Brokoli", "chicken-breast": "Naas digaag", "ground-beef": "Hilib lo'", eggs: "Ukun (duqsin)", "peanut-butter": "Botor carab (16 oz)", tuna: "Kalluun qasac (5 oz)", "lentils-dry": "Shimbra qallalan (1 lb)", "turkey-slices": "Goos goos kalluun digaag", milk: "Caano (gaalo)", "cheese-shredded": "Jiis cheddar", yogurt: "Yogurt (32 oz)", butter: "Subag (1 lb)", "cottage-cheese": "Cottage cheese (16 oz)", "rice-white": "Bariis cad (2 lb)", "rice-brown": "Bariis bunni (2 lb)", "pasta-spaghetti": "Spaghetti (1 lb)", "pasta-macaroni": "Macaroni (1 lb)", "bread-loaf": "Rooti hadhuudh", oatmeal: "Oatmeal (42 oz)", flour: "Bur (5 lb)", cereal: "Cunto quraac", "black-beans": "Digir madow (qasac)", "kidney-beans": "Digir cas (qasac)", "tomatoes-canned": "Yaanyo qasac", "tomato-sauce": "Saus yaanyo", "chicken-soup": "Maraq digaag", "vegetable-soup": "Maraq khudaar", "corn-canned": "Galley qasac", "green-beans-canned": "Digir cagaar qasac", crackers: "Biskuut", "granola-bars": "Granola bars (8)", applesauce: "Saus tufaax (6)", raisins: "Canab qallalan (12 oz)", "juice-apple": "Casiir tufaax (64 oz)", "juice-orange": "Casiir liin (64 oz)", coffee: "Bun (12 oz)", tea: "Shaah (100)", "frozen-vegetables": "Khudaar barafaysan", "frozen-fish": "Kalluun barafaysan", "frozen-pizza": "Pizza barafaysan", diapers: "Xafaayad (size 4, 28)", "soap-bar": "Saabuun (3)", toothpaste: "Macmacaan ilkaha", "toilet-paper": "Warqad musqusha (4)", "laundry-detergent": "Detergent dharka" },
  };

  function getLang() {
    const saved = localStorage.getItem(LANG_KEY);
    if (saved && UI[saved]) return saved;
    return "en";
  }

  function setLang(code) {
    if (!UI[code]) return;
    localStorage.setItem(LANG_KEY, code);
    document.documentElement.lang = code === "zh" ? "zh-Hans" : code;
    applyPage();
    document.dispatchEvent(new CustomEvent("foodbank:langchange", { detail: { lang: code } }));
  }

  function t(key, vars = {}) {
    const lang = getLang();
    let text = UI[lang]?.[key] ?? UI.en[key] ?? key;
    Object.entries(vars).forEach(([k, v]) => {
      text = text.replace(`{${k}}`, v);
    });
    return text;
  }

  function itemName(itemId, fallback = "") {
    const lang = getLang();
    return ITEMS[lang]?.[itemId] ?? ITEMS.en[itemId] ?? fallback;
  }

  function categoryName(cat) {
    const lang = getLang();
    return CATEGORIES[lang]?.[cat] ?? cat;
  }

  function unitName(unit) {
    const lang = getLang();
    return UNITS[lang]?.[unit] ?? unit;
  }

  function applyToElements() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.dataset.i18n;
      const vars = {};
      if (el.dataset.i18nLimit) vars.limit = el.dataset.i18nLimit;
      if (el.dataset.i18nWeight) vars.weight = el.dataset.i18nWeight;
      el.textContent = t(key, vars);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      el.setAttribute("aria-label", t(el.dataset.i18nAria));
    });
    document.querySelectorAll(".item-card[data-item-id]").forEach((card) => {
      const id = card.dataset.itemId;
      const nameEl = card.querySelector(".item-name");
      const catEl = card.querySelector(".item-category");
      const unitEl = card.querySelector(".item-unit");
      if (nameEl) nameEl.textContent = itemName(id, nameEl.dataset.nameEn || "");
      if (catEl) catEl.textContent = categoryName(card.dataset.category);
      if (unitEl) {
        const unit = unitEl.dataset.unit;
        const weight = unitEl.dataset.weight;
        const wLabel = getLang() === "zh" ? "磅" : "lb";
        unitEl.textContent = `${t("per_unit")} ${unitName(unit)} · ${weight} ${wLabel}`;
      }
    });
    document.querySelectorAll(".category-tab[data-category]").forEach((tab) => {
      if (tab.dataset.category === "all") {
        tab.textContent = t("all");
      } else {
        tab.textContent = categoryName(tab.dataset.category);
      }
    });
    updateLangButtons();
  }

  function updateLangButtons() {
    const current = getLang();
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === current);
      btn.setAttribute("aria-pressed", btn.dataset.lang === current ? "true" : "false");
    });
  }

  function renderLangBar() {
    const bar = document.getElementById("lang-bar");
    if (!bar) return;
    bar.innerHTML = `
      <span class="lang-bar-label" data-i18n="lang_label">${t("lang_label")}</span>
      <div class="lang-btn-group" role="group" aria-label="${t("lang_label")}">
        ${LANGS.map(
          (l) =>
            `<button type="button" class="lang-btn${l.code === getLang() ? " active" : ""}" data-lang="${l.code}" aria-pressed="${l.code === getLang()}"><span class="lang-flag">${l.flag}</span> ${l.native}</button>`
        ).join("")}
      </div>`;
    bar.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", () => setLang(btn.dataset.lang));
    });
  }

  function applyPage() {
    renderLangBar();
    applyToElements();
  }

  function init() {
    document.documentElement.lang = getLang() === "zh" ? "zh-Hans" : getLang();
    renderLangBar();
    applyToElements();
  }

  return {
    LANGS,
    getLang,
    setLang,
    t,
    itemName,
    categoryName,
    unitName,
    applyPage,
    init,
  };
})();

document.addEventListener("DOMContentLoaded", () => {
  FoodBankI18n.init();
});
