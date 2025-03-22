// AllSchedSysAd.vue
<template>
  <div class="dashboard-layout">
    <DashBoardSidebarSysAd />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="dashboard-content">
        <div class="header">
          <div class="header-left">
            <h1>All Schedules</h1>
            <p class="date">{{ formatDate(selectedDate) }}</p>
          </div>
        </div>

        <div class="main-section">
          <div class="calendar-nav">
            <div class="mini-calendar">
              <Calendar @date-selected="onDateSelected" />
            </div>
          </div>
          <div class="right-section">
            <div class="search-controls">
              <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" placeholder="Search...">
              </div>
              <div class="filter-group">
                <div class="lab-select">
                  <select v-model="selectedLab">
                    <option value="">Select Laboratory</option>
                    <option v-for="lab in laboratories" :key="lab" :value="lab">{{ lab }}</option>
                  </select>
                </div>
                <div class="section-select">
                  <select v-model="selectedSection">
                    <option value="">Select Section</option>
                    <optgroup label="BSIT">
                      <option v-for="section in bsitSections" :key="section" :value="section">{{ section }}</option>
                    </optgroup>
                    <optgroup label="BSCS">
                      <option v-for="section in bscsSections" :key="section" :value="section">{{ section }}</option>
                    </optgroup>
                  </select>
                </div>
              </div>
            </div>
            <div class="schedule-container">
              <div class="schedule-grid">
                <div class="time-column">
                  <div class="time-slot" v-for="time in timeSlots" :key="time">
                    {{ formatTime(time) }}
                  </div>
                </div>
                <div class="labs-grid">
                  <div class="lab-column" v-for="lab in ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT']" :key="lab">
                    <div class="lab-header">{{ lab }}</div>
                    <div class="lab-slots">
                      <div class="time-slot" v-for="time in timeSlots" :key="time">
                        <!-- Schedule content will go here -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebarSysAd from '../../components/DashBoardSidebarSysAd.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import Calendar from '../../components/Calendar.vue'

export default {
  name: 'AllSchedSysAd',
  components: {
    DashBoardSidebarSysAd,
    DashBoardTopbar,
    Calendar
  },
  data() {
    return {
      selectedDate: new Date(),
      selectedLab: '',
      selectedSection: '',
      laboratories: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      bsitSections: ['BSIT-1A', 'BSIT-1B', 'BSIT-2A', 'BSIT-2B', 'BSIT-3A', 'BSIT-3B', 'BSIT-4A', 'BSIT-4B'],
      bscsSections: ['BSCS-1A', 'BSCS-2A', 'BSCS-3A', 'BSCS-4A'],
      timeSlots: [
        '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00',
        '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
        '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00',
        '18:30', '19:00', '19:30', '20:00'
      ]
    }
  },
  methods: {
    onDateSelected(date) {
      this.selectedDate = date
    },
    formatDate(date) {
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
      return `${days[date.getDay()]}, ${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`
    },
    formatTime(time) {
      const [hours, minutes] = time.split(':')
      const hour = parseInt(hours)
      const ampm = hour >= 12 ? 'PM' : 'AM'
      const hour12 = hour % 12 || 12
      return `${hour12}:${minutes}${ampm}`
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

.dashboard-content {
  padding: 2rem;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

h1 {
  font-size: 2rem;
  color: #DD385A;
  margin: 0;
  font-weight: 500;
  font-family: 'Inter', sans-serif;
}

.date {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
  font-family: 'Inter', sans-serif;
}

.main-section {
  display: flex;
  gap: 2rem;
  height: calc(100% - 120px);
}

.calendar-nav {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 280px;
  height: fit-content;
}

.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-controls {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  align-items: center;
}

.filter-group {
  display: flex;
  gap: 1rem;
}

.search-box {
  position: relative;
  width: 200px;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 1rem 0.5rem 2rem;
  border: none;
  border-radius: 8px;
  background: rgba(221, 56, 90, 0.1);
  outline: none;
  font-size: 0.9rem;
  color: #DD385A;
  font-family: 'Inter', sans-serif;
}

.search-box i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(221, 56, 90, 0.6);
  font-size: 0.9rem;
}

.lab-select select,
.section-select select {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: white;
  outline: none;
  font-size: 0.9rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  min-width: 160px;
}

.lab-select select {
  color: #DD385A;
}

.section-select select {
  min-width: 180px;
  color: #333;
}

.section-select optgroup {
  font-weight: 600;
  color: #DD385A;
}

.section-select option {
  padding: 4px 8px;
  color: #DD385A;
}

.lab-select select option:first-child,
.section-select select option:first-child {
  color: #666;
}

.schedule-container {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.schedule-grid {
  display: flex;
  flex: 1;
  overflow: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(221, 56, 90, 0.6) rgba(221, 56, 90, 0.1);
}

.schedule-grid::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.schedule-grid::-webkit-scrollbar-track {
  background: rgba(221, 56, 90, 0.1);
  border-radius: 4px;
}

.schedule-grid::-webkit-scrollbar-thumb {
  background-color: rgba(221, 56, 90, 0.6);
  border-radius: 4px;
}

.labs-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  min-width: 900px;
}

.lab-column {
  border-right: 1px solid #eee;
  min-width: 150px;
  display: flex;
  flex-direction: column;
}

.lab-header {
  padding: 1rem;
  text-align: center;
  border-bottom: 1px solid #eee;
  font-weight: 500;
  color: #DD385A;
  background: #f9f9f9;
  position: sticky;
  top: 0;
  z-index: 1;
  font-family: 'Inter', sans-serif;
}

.lab-slots {
  flex: 1;
}

.time-column {
  width: 80px;
  border-right: 1px solid #eee;
  background: #f9f9f9;
  flex-shrink: 0;
}

.time-slot {
  height: 60px;
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
  color: #DD385A;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  font-family: 'Inter', sans-serif;
}

.lab-slots .time-slot {
  border-right: 1px solid #eee;
  font-family: 'Inter', sans-serif;
}
</style>