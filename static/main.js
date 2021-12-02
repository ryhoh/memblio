const getBooks = function() {
  axios
    .get('/api/v1/get/books/')
    .then(response => {
      this.books = response.data;
      this.shown_books = JSON.parse(JSON.stringify(this.books));
    })
    .catch(error => {
      console.error(error);
      this.errored = true;
    })
    .finally(() => this.loading = false);
};

const getBooksByUser = function() {
  axios
    .post('/api/v1/get/books/byuser', {}, {
      'headers': { 'Authorization': 'Bearer ' + this.token.access_token }
    })
    .then(response => {
      this.books = response.data;
      this.shown_books = JSON.parse(JSON.stringify(this.books));
    })
    .catch(error => {
      console.error(error);
      this.errored = true;
    })
    .finally(() => this.loading = false);
};

const READIN_STATES = ['stacked', 'reading', 'read'];
const filterBooks = function(filter_state) {
  if (filter_state === 'all') {
    this.shown_books = JSON.parse(JSON.stringify(this.books));
  } else {
    this.shown_books.books = this.books.books.filter(
      book => (READIN_STATES[book.is_read] === filter_state)
    );
  }
};

const rerenderFilterBooksByFlag = function(is_read_flag) {
  if (this.book_filter != 'all') {  // フィルタ使用状況に応じて，その画面を更新する
    filterBooks.bind(this)(READIN_STATES[is_read_flag]);
  } else {
    filterBooks.bind(this)('all');
  }
};

const rerenderFilterBooks = function(is_read_state) {
  filterBooks.bind(this)(is_read_state);
};


// Vue.js
const vm = new Vue({
  el: '#vue_app',

  data: () => ({
    token: {},
    user: {
      username: '',
      password: '',
    },
    books: {},
    shown_books: {},
    book_filter: 'all',
    new_book: {  // for register
      isbn13: '',
      media: '',
      owner: '',
    },
    errored: false,
    loggined: false,
  }),

  methods: {
    loginProcedure: function() {
      this.token = {
        msg: 'Processing...',
        accessing: true,
      };

      const params = new URLSearchParams();
      params.append('username', this.user.username);
      params.append('password', this.user.password);

      axios
        .post('/api/token', params)
        .then(response => {
          this.token = response.data;
          // JWT の保管
          localStorage.setItem('username', this.user.username);
          localStorage.setItem('access_token', this.token.access_token);
          localStorage.setItem('token_type', this.token.token_type);
        })
        .catch(error => {
          console.error(error);
          this.token = {
            msg: 'Login failed.',
            error: true,
          };
        });
      
      getBooksByUser.bind(this)();
    },

    updateRead: function(idx, own_id, next_is_read) {
      const params = new URLSearchParams();
      params.append('user_name', this.user.username);
      params.append('own_id', own_id);
      params.append('is_read', next_is_read);
    
      axios
        .post('/api/v1/update/read_book/', params, {
          'headers': { 'Authorization': 'Bearer ' + this.token.access_token }
        })
        .then(response => {
          old_is_read = this.books.books[idx].is_read;
          this.books.books[idx].is_read = next_is_read;
          rerenderFilterBooksByFlag.bind(this)(old_is_read);
        })
        .catch(error => {
          console.error(error);
          this.errored = true;
        })
        .finally(() => this.loading = false);
    },

    registerBook: function() {
      if (this.new_book.isbn13 === '' || this.new_book.media === '' || this.new_book.owner === '') {
        return;
      }

      const params = new URLSearchParams();
      params.append('isbn13', this.new_book.isbn13);
      params.append('media', this.new_book.media);
      params.append('owner', this.new_book.owner);
      params.append('address', this.new_book.address);
    
      axios
        .post('/api/v1/register/book/', params, {
          'headers': { 'Authorization': 'Bearer ' + this.token.access_token }
        })
        .then(response => {
          if (this.loggined) {
            getBooksByUser.bind(this)();
            this.book_filter = 'all';
            rerenderFilterBooks.bind(this)(this.book_filter);
          } else {
            getBooks.bind(this)();
          }
        })
        .catch(error => {
          console.error(error);
          this.errored = true;
        })
        .finally(() => this.loading = false);
    },
  },

  watch: {
    book_filter: function(new_val, _) {
      filterBooks.bind(this)(new_val);
    },
  },

  mounted() {
    if (localStorage.length > 0) {  // LocalStorage になにかあるなら、JWT を復旧する
      if (localStorage.getItem('username')) this.user.username = localStorage.getItem('username');
      if (localStorage.getItem('access_token')) this.token.access_token = localStorage.getItem('access_token');
      if (localStorage.getItem('token_type')) this.token.token_type = localStorage.getItem('token_type');
      this.loggined = true;
      getBooksByUser.bind(this)();
      return;
    }
    getBooks.bind(this)();
  },
});
  