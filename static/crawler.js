
const Cralwer = {
    async checkAuth(id, password) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: 'https://api.hanyang.ac.kr/oauth/login_submit.json',
                data: {
                    _userId: id,
                    _password: password,
                    identck: 'mobile_002',
                    sinbun: '',
                },
                cache: false,
		        async: false,
                type: 'POST',
                success: function(data) {
                    resolve(data)
                }
            })
        })
    },

    async getSch(id, password) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/assignment',
                data: {
                    userId: id,
                    password: password,
                },
                cache: false,
		        async: true,
                type: 'GET',
                success: function(data) {
                    resolve(data)
                },
                error: reject
            })
        })
    }
}