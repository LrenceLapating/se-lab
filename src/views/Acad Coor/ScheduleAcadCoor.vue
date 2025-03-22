<template>
    <div class="dashboard-layout">
      <DashBoardSidebar />
      <div class="main-content">
        <DashBoardTopbar />
        <div class="schedule-content">
          <div class="header">
            <div class="user-info">
              <div class="info-row">
                <span class="label">ID Number:</span>
                <span class="value">{{ user.idNumber }}</span>
              </div>
              <div class="info-row">
                <span class="label">Name:</span>
                <span class="value">{{ user.name }}</span>
              </div>
              <div class="info-row">
                <span class="label">Classification:</span>
                <span class="value">{{ user.classification }}</span>
              </div>
              <p class="current-date">{{ weekDateRange }}</p>
            </div>
          </div>
  
          <div class="schedule-actions">
            <div class="week-navigation">
              <button class="nav-btn" @click="previousWeek">
                <i class="pi pi-angle-left"></i>
              </button>
              <button class="nav-btn" @click="nextWeek">
                <i class="pi pi-angle-right"></i>
              </button>
            </div>
            <button class="btn-action">
              <i class="fas fa-download"></i>
              Download Schedule
            </button>
          </div>
  
          <div class="schedule-container">
            <div class="schedule-card">
              <div class="schedule-header">
                <h2>Current Week</h2>
              </div>
              
              <div class="schedule-table">
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th v-for="(day, index) in weekDays" :key="day.name">
                        <div class="day-header">
                          <span class="day-name">{{ day.name }}</span>
                          <span class="day-date">{{ day.date }}</span>
                        </div>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="time in timeSlots" :key="time">
                      <td class="time-slot">{{ time }}</td>
                      <td v-for="day in weekDays" 
                          :key="day.name" 
                          class="schedule-slot">
                        <!-- Schedule items will be dynamically populated here -->
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import DashBoardSidebar from '../../components/DashBoardSidebarAcadCoor.vue'
  import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
  
  export default {
    name: 'ScheduleAcadCoor',
    components: {
      DashBoardSidebar,
      DashBoardTopbar
    },
    data() {
      return {
        user: {
          idNumber: '',
          name: '',
          classification: ''
        },
        currentWeekStart: new Date(),
        timeSlots: [
          '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', 
          '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM',
          '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
          '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM',
          '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM',
          '8:00 PM'
        ],
        weekDays: []
      }
    },
    methods: {
      formatCurrentDate() {
        const today = new Date();
        return today.toLocaleDateString('en-US', { 
          weekday: 'long',
          month: 'long',
          day: 'numeric',
          year: 'numeric'
        });
      },
      previousWeek() {
        const newDate = new Date(this.currentWeekStart);
        newDate.setDate(newDate.getDate() - 7);
        this.currentWeekStart = newDate;
      },
      nextWeek() {
        const newDate = new Date(this.currentWeekStart);
        newDate.setDate(newDate.getDate() + 7);
        this.currentWeekStart = newDate;
      },
      getWeekDays() {
        const days = [];
        const monday = new Date(this.currentWeekStart);
        // Adjust to Monday of the week
        monday.setDate(monday.getDate() - monday.getDay() + 1);
  
        for (let i = 0; i < 5; i++) {
          const date = new Date(monday);
          date.setDate(monday.getDate() + i);
          days.push({
            name: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][i],
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
          });
        }
        return days;
      }
    },
    computed: {
      weekDateRange() {
        const days = this.getWeekDays();
        const firstDay = days[0].date;
        const lastDay = days[4].date;
        const [firstMonth, firstDate] = firstDay.split(' ');
        const [lastMonth, lastDate] = lastDay.split(' ');
        
        // If same month, show only once
        if (firstMonth === lastMonth) {
          return `${firstMonth} ${firstDate} - ${lastDate}, 2025`;
        }
        return `${firstMonth} ${firstDate} - ${lastMonth} ${lastDate}, 2025`;
      }
    },
    watch: {
      currentWeekStart: {
        handler() {
          this.weekDays = this.getWeekDays();
        },
        immediate: true
      }
    }
  }
  </script>
  
  <style scoped>
  .dashboard-layout {
    display: flex;
    width: 100vw;
    height: 100vh;
    background-color: #f5f5f5;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
  }
  
  .main-content {
    flex: 1;
    margin-left: 70px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .schedule-content {
    padding: 1.5rem;
    height: calc(100vh - 64px);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #DD385A rgba(221, 56, 90, 0.1);
  }
  
  .schedule-content::-webkit-scrollbar {
    width: 8px;
  }
  
  .schedule-content::-webkit-scrollbar-track {
    background: rgba(221, 56, 90, 0.1);
    border-radius: 4px;
  }
  
  .schedule-content::-webkit-scrollbar-thumb {
    background-color: #DD385A;
    border-radius: 4px;
  }
  
  .header {
    margin-bottom: 1rem;
  }
  
  .user-info {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .info-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
    align-items: center;
  }
  
  .info-row:last-of-type {
    margin-bottom: 1rem;
  }
  
  .label {
    color: #666;
    font-size: 0.9rem;
    min-width: 100px;
  }
  
  .value {
    color: #333;
    font-weight: 500;
    font-size: 0.95rem;
  }
  
  .current-date {
    color: #DD385A;
    font-size: 0.9rem;
    margin: 0;
    padding-top: 0.5rem;
    border-top: 1px solid #eee;
  }
  
  .schedule-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .week-navigation {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 6px;
    background-color: #DD385A;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .nav-btn:hover {
    background-color: #c62f4d;
    transform: translateY(-1px);
  }
  
  .schedule-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  
  .schedule-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .schedule-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .schedule-header h2 {
    color: #333;
    margin: 0;
    font-size: 1.5rem;
    font-weight: 500;
  }
  
  .schedule-actions {
    display: flex;
    gap: 1rem;
  }
  
  .btn-action {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    border: none;
    border-radius: 8px;
    background-color: #DD385A;
    color: white;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .btn-action:hover {
    background-color: #c62f4d;
    transform: translateY(-1px);
  }
  
  .btn-action i {
    font-size: 1rem;
  }
  
  .schedule-table {
    flex: 1;
    overflow: auto;
    scrollbar-width: thin;
    scrollbar-color: #DD385A rgba(221, 56, 90, 0.1);
    position: relative;
    height: calc(100vh - 200px);
  }
  
  .schedule-table::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .schedule-table::-webkit-scrollbar-track {
    background: rgba(221, 56, 90, 0.1);
    border-radius: 4px;
  }
  
  .schedule-table::-webkit-scrollbar-thumb {
    background-color: #DD385A;
    border-radius: 4px;
  }
  
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    min-width: 800px;
  }
  
  th, td {
    border: 1px solid #eee;
    padding: 1rem;
    text-align: center;
    background-color: white;
    height: 60px;
  }
  
  th {
    background-color: #DD385A;
    color: white;
    font-weight: 500;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  th:first-child {
    left: 0;
    z-index: 20;
  }
  
  td:first-child {
    position: sticky;
    left: 0;
    z-index: 5;
    background-color: rgba(221, 56, 90, 0.05);
    color: #DD385A;
    font-weight: 500;
  }
  
  .day-header {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    align-items: center;
    position: relative;
  }
  
  /* Add shadow effects for sticky elements */
  th::after, td:first-child::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 4px;
    pointer-events: none;
    box-shadow: inset -2px 0 4px -2px rgba(0, 0, 0, 0.1);
  }
  
  th:first-child::after {
    box-shadow: none;
  }
  
  /* Add bottom shadow for header row */
  thead::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 4px;
    pointer-events: none;
    box-shadow: inset 0 -2px 4px -2px rgba(0, 0, 0, 0.1);
  }
  
  .day-name {
    font-size: 1rem;
  }
  
  .day-date {
    font-size: 0.8rem;
    opacity: 0.9;
  }
  
  .time-slot {
    color: #DD385A;
    font-weight: 500;
    background-color: rgba(221, 56, 90, 0.05);
  }
  
  .schedule-slot {
    background-color: white;
    transition: background-color 0.2s ease;
  }
  
  .schedule-slot:hover {
    background-color: rgba(221, 56, 90, 0.05);
  }
  </style>