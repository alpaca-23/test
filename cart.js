(function () {
  var KEY = 'tairou_cart';

  window.CartStore = {
    get: function () {
      try { return JSON.parse(localStorage.getItem(KEY)) || []; }
      catch (e) { return []; }
    },
    save: function (items) {
      localStorage.setItem(KEY, JSON.stringify(items));
    },
    add: function (item) {
      var cart = this.get();
      var idx = cart.findIndex(function (i) {
        return i.item_cd === item.item_cd &&
               i.housoushi === item.housoushi &&
               i.noshi === item.noshi;
      });
      if (idx >= 0) {
        cart[idx].qty += item.qty;
      } else {
        cart.push(item);
      }
      this.save(cart);
    },
    count: function () {
      return this.get().reduce(function (s, i) { return s + i.qty; }, 0);
    }
  };

  window.addToCartFromForm = function (form) {
    var item = {
      item_cd:    form.item_cd.value,
      item_nm:    form.item_nm.value,
      price:      parseInt(form.price.value, 10),
      housoushi:  form.housoushi ? form.housoushi.value : '包装紙なし',
      noshi:      form.noshi     ? form.noshi.value     : 'のし紙なし',
      qty:        parseInt(form.qty.value, 10) || 1
    };
    CartStore.add(item);
    window.location.href = 'cart.html';
  };

  /* ナビのカートバッジを更新 */
  document.addEventListener('DOMContentLoaded', function () {
    var count = CartStore.count();
    var badge = document.getElementById('cart-count');
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }
  });
})();
