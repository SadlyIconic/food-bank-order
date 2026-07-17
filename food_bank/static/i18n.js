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
      nav_status: "Status",
      nav_give: "Give",
      nav_give_needs: "Needs board",
      nav_give_pledge: "Make a pledge",
      nav_admin: "Admin",
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
      household_label: "Household / name",
      household_optional: "(optional)",
      household_placeholder: "e.g. Smith family",
      review_order: "Review order",
      cart_empty: "Your cart is empty.",
      start_shopping: "Start shopping",
      confirm_title: "Confirm your order",
      confirm_subtitle: "Check everything looks right, then place your order.",
      ordering_for: "Ordering for:",
      back_to_cart: "Back to cart",
      place_order: "Place order",
      confirm_empty: "Nothing to confirm — your cart is empty.",
      go_to_shop: "Go to shop",
      status_title: "Order status",
      status_subtitle: "See what your household can receive this trip.",
      status_lookup: "Look up",
      status_placeholder: "Enter the name you used when ordering",
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
      status_pending: "Orders are in — pickup planning is not finished yet. Check back after the food bank plans this trip.",
      status_not_found: "No order found for this name in the current round. Check spelling or ask the food bank if orders are still open.",
      community_app_name: "Community Give",
      community_nav_board: "Needs board",
      community_nav_pledge: "Pledge",
      community_needs_title: "This trip's remaining needs",
      community_needs_subtitle: "Help fill gaps after the food bank's pickup run. No login required.",
      community_pickup: "Pickup",
      community_not_recorded: "Fulfillment has not been recorded yet. Check back after the food bank plans this trip.",
      community_unpublished: "The community board is being prepared. Check back soon.",
      community_title: "This trip's remaining needs",
      community_subtitle: "Help fill gaps after pickup planning. No account needed.",
      community_not_ready: "Fulfillment has not been recorded yet. Check back after the food bank plans this trip.",
      community_not_published: "The needs board is not published yet. Check back soon.",
      community_all_covered: "All needs are covered for this trip. Thank you!",
      community_pledge_btn: "Make a pledge",
      community_make_pledge: "Make a pledge",
      community_open_needs: "Open needs",
      community_needed: "Needed",
      community_pledged: "Pledged",
      community_still_open: "Still open",
      community_picked: "Picked",
      community_legend_picked: "Picked",
      community_legend_pledged: "Pledged",
      community_legend_open: "Still open",
      community_thanks_title: "Community thanks",
      community_thanks_body: "Donors who pledged this trip:",
      community_pledge_board: "Pledge board",
      community_pledge_board_sub: "Thank you to everyone contributing this trip.",
      community_donor: "Donor",
      community_donor_name: "Your name",
      community_note: "Note",
      community_no_open_items: "Nothing open for pledges right now — thank you!",
      community_pledge_title: "Make a pledge",
      community_pledge_subtitle: "Tell us what you'll bring. Use your first name or choose anonymous.",
      community_back_board: "Back to needs board",
      community_donor_placeholder: "e.g. Maria",
      community_anonymous: "Anonymous donor",
      community_note_placeholder: "e.g. I'll drop off Saturday morning",
      community_submit_pledge: "Submit pledge",
      community_remaining_hint: "Up to {count} still open for this item.",
      community_option_label: "{name} — {count} {unit} still open",
    },
    es: {
      app_name: "Pedido del Banco de Alimentos",
      nav_shop: "Tienda",
      nav_cart: "Carrito",
      nav_status: "Estado",
      nav_give: "Donar",
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
      household_label: "Hogar / nombre",
      household_optional: "(opcional)",
      household_placeholder: "ej. Familia García",
      review_order: "Revisar pedido",
      cart_empty: "Su carrito está vacío.",
      start_shopping: "Empezar a comprar",
      confirm_title: "Confirmar pedido",
      confirm_subtitle: "Verifique que todo esté correcto y luego confirme.",
      ordering_for: "Pedido para:",
      back_to_cart: "Volver al carrito",
      place_order: "Realizar pedido",
      confirm_empty: "Nada que confirmar — su carrito está vacío.",
      go_to_shop: "Ir a la tienda",
      status_title: "Estado del pedido",
      status_subtitle: "Vea lo que su hogar puede recibir en este viaje.",
      status_lookup: "Buscar",
      status_placeholder: "Ingrese el nombre que usó al pedir",
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
      community_app_name: "Comunidad — Donar",
      community_nav_board: "Necesidades",
      community_nav_pledge: "Comprometerse",
      community_title: "Necesidades restantes de este viaje",
      community_subtitle: "Ayude a cubrir faltantes después de la planificación. No necesita cuenta.",
      community_not_ready: "Aún no se ha registrado el cumplimiento. Vuelva después de que el banco planifique el viaje.",
      community_not_published: "El tablero de necesidades aún no está publicado. Vuelva pronto.",
      community_all_covered: "Todas las necesidades están cubiertas. ¡Gracias!",
      community_pledge_btn: "Hacer un compromiso",
      community_needed: "Necesario",
      community_pledged: "Comprometido",
      community_still_open: "Aún abierto",
      community_picked: "Recogido",
      community_pledge_board: "Compromisos de la comunidad",
      community_pledge_board_sub: "Gracias a todos los que contribuyen en este viaje.",
      community_donor: "Donante",
      community_note: "Nota",
      community_pledge_title: "Hacer un compromiso",
      community_pledge_subtitle: "Díganos qué traerá. Use su nombre o elija anónimo.",
      community_back_board: "Volver al tablero",
      community_donor_placeholder: "ej. María",
      community_anonymous: "Donante anónimo",
      community_note_placeholder: "ej. Lo dejaré el sábado por la mañana",
      community_submit_pledge: "Enviar compromiso",
      community_remaining_hint: "Aún faltan hasta {count} para este artículo.",
      community_option_label: "{name} — faltan {count} {unit}",
    },
    zh: {
      app_name: "食物银行订购",
      nav_shop: "选购",
      nav_cart: "购物车",
      nav_status: "订单状态",
      nav_give: "捐赠",
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
      household_label: "家庭 / 姓名",
      household_optional: "（可选）",
      household_placeholder: "例如：张家",
      review_order: "核对订单",
      cart_empty: "购物车是空的。",
      start_shopping: "开始选购",
      confirm_title: "确认订单",
      confirm_subtitle: "请确认无误后提交订单。",
      ordering_for: "订购人：",
      back_to_cart: "返回购物车",
      place_order: "提交订单",
      confirm_empty: "无需确认 — 购物车是空的。",
      go_to_shop: "去选购",
      status_title: "订单状态",
      status_subtitle: "查看本次领取您家可以获得什么。",
      status_lookup: "查询",
      status_placeholder: "输入下单时使用的姓名",
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
      community_nav_board: "需求板",
      community_nav_pledge: "承诺捐赠",
      community_title: "本次行程剩余需求",
      community_subtitle: "在取货计划完成后帮助填补缺口。无需账户。",
      community_not_ready: "尚未记录配送情况。请在食物银行完成计划后再查看。",
      community_not_published: "需求板尚未发布。请稍后再来。",
      community_all_covered: "本次行程所有需求已满足。谢谢！",
      community_pledge_btn: "承诺捐赠",
      community_needed: "需要",
      community_pledged: "已承诺",
      community_still_open: "仍缺",
      community_picked: "已取",
      community_pledge_board: "社区捐赠承诺",
      community_pledge_board_sub: "感谢所有为本次行程贡献的人。",
      community_donor: "捐赠者",
      community_note: "备注",
      community_pledge_title: "承诺捐赠",
      community_pledge_subtitle: "告诉我们您将带来什么。可使用名字或选择匿名。",
      community_back_board: "返回需求板",
      community_donor_placeholder: "例如：张",
      community_anonymous: "匿名捐赠",
      community_note_placeholder: "例如：周六上午送达",
      community_submit_pledge: "提交承诺",
      community_remaining_hint: "此物品仍缺最多 {count}。",
      community_option_label: "{name} — 仍缺 {count} {unit}",
    },
    vi: {
      app_name: "Đặt hàng Ngân hàng Thực phẩm",
      nav_shop: "Mua sắm",
      nav_cart: "Giỏ hàng",
      nav_status: "Trạng thái",
      nav_give: "Quyên góp",
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
      household_label: "Hộ gia đình / tên",
      household_optional: "(tuỳ chọn)",
      household_placeholder: "vd. Gia đình Nguyễn",
      review_order: "Xem lại đơn",
      cart_empty: "Giỏ hàng trống.",
      start_shopping: "Bắt đầu mua",
      confirm_title: "Xác nhận đơn hàng",
      confirm_subtitle: "Kiểm tra kỹ rồi đặt hàng.",
      ordering_for: "Đặt cho:",
      back_to_cart: "Quay lại giỏ",
      place_order: "Đặt hàng",
      confirm_empty: "Không có gì để xác nhận — giỏ trống.",
      go_to_shop: "Đi mua sắm",
      status_title: "Trạng thái đơn hàng",
      status_subtitle: "Xem hộ gia đình bạn nhận được gì trong chuyến này.",
      status_lookup: "Tra cứu",
      status_placeholder: "Nhập tên bạn dùng khi đặt hàng",
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
      community_nav_board: "Nhu cầu",
      community_nav_pledge: "Cam kết",
      community_title: "Nhu cầu còn lại chuyến này",
      community_subtitle: "Giúp lấp đầy sau khi lên kế hoạch lấy hàng. Không cần tài khoản.",
      community_not_ready: "Chưa ghi nhận hoàn thành. Hãy quay lại sau khi ngân hàng thực phẩm lên kế hoạch.",
      community_not_published: "Bảng nhu cầu chưa được công bố. Hãy quay lại sau.",
      community_all_covered: "Mọi nhu cầu đã được đáp ứng. Cảm ơn!",
      community_pledge_btn: "Cam kết quyên góp",
      community_needed: "Cần",
      community_pledged: "Đã cam kết",
      community_still_open: "Còn thiếu",
      community_picked: "Đã lấy",
      community_pledge_board: "Cam kết cộng đồng",
      community_pledge_board_sub: "Cảm ơn mọi người đóng góp chuyến này.",
      community_donor: "Người quyên góp",
      community_note: "Ghi chú",
      community_pledge_title: "Cam kết quyên góp",
      community_pledge_subtitle: "Cho chúng tôi biết bạn sẽ mang gì. Dùng tên hoặc chọn ẩn danh.",
      community_back_board: "Quay lại bảng nhu cầu",
      community_donor_placeholder: "vd. Lan",
      community_anonymous: "Ẩn danh",
      community_note_placeholder: "vd. Tôi sẽ giao sáng thứ Bảy",
      community_submit_pledge: "Gửi cam kết",
      community_remaining_hint: "Còn thiếu tối đa {count} cho mặt hàng này.",
      community_option_label: "{name} — còn thiếu {count} {unit}",
    },
    tl: {
      app_name: "Order sa Food Bank",
      nav_shop: "Mamili",
      nav_cart: "Cart",
      nav_status: "Status",
      nav_give: "Magbigay",
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
      household_label: "Sambahayan / pangalan",
      household_optional: "(opsyonal)",
      household_placeholder: "hal. Pamilya Santos",
      review_order: "Suriin ang order",
      cart_empty: "Walang laman ang cart.",
      start_shopping: "Magsimulang mamili",
      confirm_title: "Kumpirmahin ang order",
      confirm_subtitle: "Siguraduhing tama ang lahat bago mag-order.",
      ordering_for: "Order para kay:",
      back_to_cart: "Bumalik sa cart",
      place_order: "Mag-order",
      confirm_empty: "Walang ikukumpirma — walang laman ang cart.",
      go_to_shop: "Pumunta sa tindahan",
      status_title: "Status ng order",
      status_subtitle: "Tingnan kung ano ang matatanggap ng inyong sambahayan.",
      status_lookup: "Hanapin",
      status_placeholder: "Ilagay ang pangalang ginamit ninyo",
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
      community_app_name: "Komunidad — Magbigay",
      community_nav_board: "Mga pangangailangan",
      community_nav_pledge: "Mag-pledge",
      community_title: "Natitirang pangangailangan sa biyaheng ito",
      community_subtitle: "Tumulong punan ang kulang pagkatapos ng pickup planning. Walang account na kailangan.",
      community_not_ready: "Hindi pa naitala ang fulfillment. Bumalik pagkatapos planuhin ng food bank ang biyahe.",
      community_not_published: "Hindi pa nai-publish ang needs board. Bumalik muli.",
      community_all_covered: "Lahat ng pangangailangan ay natugunan. Salamat!",
      community_pledge_btn: "Mag-pledge",
      community_needed: "Kailangan",
      community_pledged: "Na-pledge",
      community_still_open: "Bukas pa",
      community_picked: "Nakuha",
      community_pledge_board: "Mga pledge ng komunidad",
      community_pledge_board_sub: "Salamat sa lahat ng nag-aambag sa biyaheng ito.",
      community_donor: "Donor",
      community_note: "Tala",
      community_pledge_title: "Mag-pledge",
      community_pledge_subtitle: "Sabihin kung ano ang dadalhin ninyo. Gamitin ang pangalan o piliin ang anonymous.",
      community_back_board: "Bumalik sa needs board",
      community_donor_placeholder: "hal. Maria",
      community_anonymous: "Anonymous na donor",
      community_note_placeholder: "hal. Idedrop off ko Sabado ng umaga",
      community_submit_pledge: "Isumite ang pledge",
      community_remaining_hint: "Hanggang {count} pa ang bukas para sa item na ito.",
      community_option_label: "{name} — {count} {unit} pa ang bukas",
    },
    so: {
      app_name: "Dalabka Bangiga Cuntada",
      nav_shop: "Iibso",
      nav_cart: "Gaariga",
      nav_status: "Xaaladda",
      nav_give: "Bixi",
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
      household_label: "Qoyska / magaca",
      household_optional: "(ikhtiyaari)",
      household_placeholder: "tusaale Qoyska Ali",
      review_order: "Hubi dalabka",
      cart_empty: "Gaarigu waa madhan yahay.",
      start_shopping: "Bilow iibsiga",
      confirm_title: "Xaqiiji dalabka",
      confirm_subtitle: "Hubi in wax walba sax yihiin ka dibna dalbo.",
      ordering_for: "Dalab loogu talagalay:",
      back_to_cart: "Ku noqo gaariga",
      place_order: "Dalbo",
      confirm_empty: "Wax xaqiijin ah ma jiro — gaarigu waa madhan.",
      go_to_shop: "Tag dukaanka",
      status_title: "Xaaladda dalabka",
      status_subtitle: "Eeg waxa qoyskaagu ka heli karo safarkan.",
      status_lookup: "Raadi",
      status_placeholder: "Geli magaca aad dalbaneysay",
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
      community_nav_board: "Baahida",
      community_nav_pledge: "Ballanqaad",
      community_title: "Baahiyaha ka haray safarkan",
      community_subtitle: "Ka caawi buuxinta ka dib qorsheynta soo qaadista. Akoon looma baahna.",
      community_not_ready: "Fulfillment weli lama diiwaangelin. Soo noqo ka dib marka bangiga cuntadu qorsheeyo safarka.",
      community_not_published: "Guddiga baahida weli lama daabacin. Soo noqo dhowaan.",
      community_all_covered: "Dhammaan baahiyaha waa la daboolay. Mahadsanid!",
      community_pledge_btn: "Ballanqaad bixin",
      community_needed: "Loo baahan yahay",
      community_pledged: "La ballanqaaday",
      community_still_open: "Wali furan",
      community_picked: "La soo qaatay",
      community_pledge_board: "Ballanqaadyada bulshada",
      community_pledge_board_sub: "Mahadsanid dhammaan kuwa ka qayb qaata safarkan.",
      community_donor: "Bixiye",
      community_note: "Qoraal",
      community_pledge_title: "Ballanqaad bixin",
      community_pledge_subtitle: "Noo sheeg waxaad keeni doontid. Isticmaal magacaaga ama dooro qarsoodi.",
      community_back_board: "Ku noqo guddiga baahida",
      community_donor_placeholder: "tusaale Amina",
      community_anonymous: "Bixiye qarsoodi ah",
      community_note_placeholder: "tusaale Sabtida subaxdii waan keeni doonaa",
      community_submit_pledge: "Gudbi ballanqaadka",
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
