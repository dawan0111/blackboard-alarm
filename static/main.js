

(async function() {
    const USER_ID = localStorage.getItem('_userId');
    const DECODE_USER_ID = localStorage.getItem('_decodeUserId')
    const USER_PW = localStorage.getItem('_userPassword');

    if (!(USER_ID || USER_PW)) {
        location.href = '/login';
        return;
    }

    var app = new Vue({
        el: '#app',
        data: {
            assignments: [],
            standardDate: null,
        },

        created () {
            this.fetchAssignments();
            standardDate = moment().format("YY년 MM월 DD일 HH시 mm분 기준");
        },

        methods: {
            async fetchAssignments() {
                const schList = await Cralwer.getSch(USER_ID, USER_PW, DECODE_USER_ID);

                this.assignments = schList.data
                    .filter(sch => (+new Date() - new Date(sch.endDate)) < 0)
                    .map(sch => {
                        const endDate = new Date(sch.endDate);
                        const diffHour = moment(endDate).diff(moment(), 'hours');
                        const diffMinute = moment(endDate).diff(moment(), 'minutes');

                        sch.endTimeStamp = +endDate;
                        sch.endDateFormat = moment(endDate).format("YY년 MM월 DD일 HH시 mm분"); 
                        sch.someTimeStamp = sch.endTimeStamp - (+new Date());
                        sch.isEnd = (+new Date() - endDate) >= 0;
                        sch.badge = diffHour >= 24 ? `${Math.floor(diffHour / 24)}일 ${diffHour % 24}시간 남음` : `${Math.floor(diffMinute / 60)}시 ${diffMinute % 60}분 남음`;
                        sch.attempts = []
                        sch.noAttempt = false

                        return sch;
                    })
                    .sort((a, b) => {
                        return a.someTimeStamp - b.someTimeStamp;
                    })

                for await (schs of _.chunk(this.assignments, 3)) {
                    const values = await Promise.all(
                        schs.map(sch => ($.ajax(
                            {
                                url: '/assignment-detail',
                                data: {
                                    calendarId: sch.calendarId,
                                    itemSourceId: sch.itemSourceId
                                },
                                type: "GET"
                            }
                        )))
                    )
                    
                    const responseData = values.reduce((acc, val) => ({
                        ...acc,
                        [val.data.itemSourceId]: val.data.status
                    }), {})

                    this.assignments = this.assignments.map((sch) => {
                        if (responseData[sch.itemSourceId]) {
                            sch.attemptStatus = responseData[sch.itemSourceId]
                            sch.noAttempt = sch.attemptStatus == "IN_PROGRESS"
                        }
                        return sch;
                    })
                };
            }
        }
      })
})()