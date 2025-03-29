<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSideBarDean />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <div class="header-content">
              <h2>Schedules Approval</h2>
              <div class="action-buttons" v-if="hasPendingSchedules">
                <button class="clear-btn" @click="clearAllSchedules">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                  </svg>
                  Clear All
                </button>
                <button class="approve-btn" @click="approveSelectedSchedule">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 6L9 17l-5-5"/>
                  </svg>
                  Approve All
                </button>
                <button class="reject-btn" @click="rejectSelectedSchedule">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Reject All
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="dashboard-content">
          <div class="right-panel">
            <div class="controls-top">
              <div class="search-box">
                <span class="search-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>
                </span>
                <input type="text" placeholder="Search..." />
              </div>
              
              <div class="semester-dropdown-wrapper">
                <select v-model="selectedSemester" class="semester-dropdown">
                  <option v-for="semester in semesters" :key="semester" :value="semester">{{ semester }}</option>
                </select>
              </div>

              <div class="lab-dropdown-wrapper">
                <select v-model="selectedLab" class="lab-dropdown">
                  <option v-for="lab in labs" :key="lab" :value="lab">{{ lab }}</option>
                </select>
              </div>
            </div>

            <div class="schedule-container">
              <div class="schedule-table">
                <div class="table-header">
                  <div class="time-header">Time</div>
                  <div class="day-headers">
                    <div class="day-header" v-for="(day, index) in weekDays" :key="index">
                      <div class="day-name">{{ day.name }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="table-body">
                  <div class="time-column">
                    <div class="time-slot" v-for="time in displayTimeSlots" :key="time">
                      {{ time }}
                    </div>
                  </div>
                  
                  <div class="days-grid">
                    <div class="day-column" v-for="(day, dayIndex) in weekDays" :key="dayIndex">
                      <div class="time-slots">
                        <div class="slot" v-for="(time, timeIndex) in displayTimeSlots" :key="timeIndex">
                          <div 
                            v-if="isTimeSlotWithinSchedule(day.name, time)"
                            class="schedule-item" 
                            :class="getScheduleStatusClass(day.name, time)"
                          >
                            <div 
                              v-if="isScheduleStart(day.name, time)" 
                              class="schedule-content"
                              @click="showScheduleDetails(day.name, time)"
                            >
                              <div class="schedule-lab">{{ selectedLab }}</div>
                              <div class="schedule-time">{{ getScheduleTime(day.name, time) }}</div>
                              <div class="schedule-title">{{ getScheduleTitle(day.name, time) }}</div>
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
      </div>
    </div>

    <!-- Schedule Details Popup -->
    <div class="schedule-popup" v-if="showPopup">
      <div class="popup-content">
        <div class="popup-header">
          <h3>{{ selectedSchedule.title }}</h3>
          <button class="close-btn" @click="closePopup">×</button>
        </div>
        <div class="popup-body">
          <div class="detail-row">
            <span class="detail-label">Lab:</span>
            <span class="detail-value">{{ selectedSchedule.labRoom }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Course:</span>
            <span class="detail-value">{{ selectedSchedule.courseName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Section:</span>
            <span class="detail-value">{{ selectedSchedule.section }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Instructor:</span>
            <span class="detail-value">{{ selectedSchedule.instructorName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Time:</span>
            <span class="detail-value">{{ selectedSchedule.startTime }} - {{ selectedSchedule.endTime }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Day:</span>
            <span class="detail-value">{{ selectedSchedule.day }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSideBarDean from '../../components/DashBoardSideBarDean.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'AllSchedSysAd',
  components: {
    DashBoardSideBarDean,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: 'L201',
      labs: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      selectedSemester: '1st Sem 2025-2026',
      semesters: [
        '1st Sem 2025-2026',
        '2nd Sem 2025-2026',
        'Summer 2026',
        '1st Sem 2026-2027',
        '2nd Sem 2026-2027',
        'Summer 2027'
      ],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM',
        '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM',
        '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM',
        '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM',
        '7:30 PM', '8:00 PM'
      ],
      schedules: [],
      allSchedules: [], // To store all schedules before filtering
      weekDays: [],
      showPopup: false,
      selectedSchedule: {},
      userName: 'User',
      pollInterval: null, // For storing the polling interval
      lastUpdateTimestamp: null // To track the last update time
    }
  },
  created() {
    this.checkAuth();
    // Start polling for updates
    this.startPolling();
  },
  beforeDestroy() {
    // Clean up polling when component is destroyed
    this.stopPolling();
  },
  mounted() {
    this.checkAuth();
    this.getUserName();
    this.loadSchedulesFromStorage();
    this.generateWeekDays();
    this.loadPendingSchedules();
    this.loadRegistrationRequests();
  },
  watch: {
    selectedSemester: {
      handler(newSemester) {
        this.filterSchedulesBySemester();
      },
      immediate: true
    }
  },
  computed: {
    hasPendingSchedules() {
      return this.allSchedules.some(schedule => 
        schedule.status === 'pending' &&
        schedule.semester === this.selectedSemester
      );
    }
  },
  methods: {
    checkAuth() {
      // Check if user is authenticated and has the correct role
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.error('No authentication found, redirecting to login');
        this.$router.push('/login');
        return;
      }
      
      try {
        const userData = JSON.parse(userStr);
        
        // Verify the user has either System Administrator or Dean role
        if (userData.role !== 'System Administrator' && userData.role !== 'Dean') {
          console.error('User does not have permission to view this page');
          // Redirect to the appropriate dashboard based on role
          if (userData.role === 'Academic Coordinator') {
            this.$router.push('/dashboard-acad-coor');
          } else if (userData.role === 'Lab InCharge') {
            this.$router.push('/dashboard-lab');
          } else {
            this.$router.push('/dashboard-viewer');
          }
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.$router.push('/login');
      }
    },
    getUserName() {
      // Get user data from session or local storage
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      if (userStr) {
        try {
          const userData = JSON.parse(userStr);
          if (userData.full_name) {
            // Get first name only
            this.userName = userData.full_name.split(' ')[0];
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    },
    previousLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex > 0) {
        this.selectedLab = this.labs[currentIndex - 1]
      }
    },
    nextLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex < this.labs.length - 1) {
        this.selectedLab = this.labs[currentIndex + 1]
      }
    },
    generateWeekDays() {
      // Simply use the fixed days without dates
      this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(name => {
        return { name }
      });
    },
    isTimeSlotInSchedule(timeSlot, startTime, endTime) {
      try {
        // Convert timeSlot, startTime, and endTime to minutes for easy comparison
        const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
        const startTimeMinutes = this.convertTimeToMinutes(startTime);
        const endTimeMinutes = this.convertTimeToMinutes(endTime);
        
        // Check if timeSlot is within or at the start of the schedule
        return timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes;
      } catch (error) {
        console.error('Error checking if time slot is in schedule:', error);
        return false;
      }
    },
    convertTimeToMinutes(time) {
      try {
        // Parse time string (format: "HH:MM AM/PM")
        const [hourStr, minutePeriodStr] = time.split(':');
        if (!minutePeriodStr) {
          console.error('Invalid time format:', time);
          return 0;
        }
        
        const minutePeriod = minutePeriodStr.trim();
        const minuteStr = minutePeriod.split(' ')[0];
        const period = minutePeriod.split(' ')[1];
        
        if (!hourStr || !minuteStr || !period) {
          console.error('Invalid time components:', { hourStr, minuteStr, period });
          return 0;
        }
        
        let hour = parseInt(hourStr);
        const minute = parseInt(minuteStr);
        
        // Convert to 24-hour format
        if (period === 'PM' && hour < 12) hour += 12;
        if (period === 'AM' && hour === 12) hour = 0;
        
        const totalMinutes = hour * 60 + minute;
        
        // Return total minutes
        return totalMinutes;
      } catch (error) {
        console.error('Error converting time to minutes:', time, error);
        return 0;
      }
    },
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Include the ending time slot as well
        return timeSlotMinutes >= startMinutes && timeSlotMinutes <= endMinutes;
      });
    },
    isScheduleStart(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        return timeSlotMinutes === startMinutes;
      });
    },
    getScheduleTitle(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return relevantSchedules[0].title;
    },
    getScheduleTime(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return `${relevantSchedules[0].startTime} - ${relevantSchedules[0].endTime}`;
    },
    getScheduleDetails(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      
      const schedule = relevantSchedules[0];
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    getScheduleStatusClass(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Include the ending time slot as well
        return slotMinutes >= startMinutes && slotMinutes <= endMinutes;
      });
      
      if (!schedule) return '';
      
      // Return the appropriate class for the schedule status
      switch (schedule.status) {
        case 'draft':
          return 'status-draft';
        case 'pending':
          return 'status-pending';
        case 'approved':
          return 'status-approved';
        default:
          return 'status-approved';
      }
    },
    loadSchedulesFromStorage() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading schedules');
          return;
        }

        // Initialize empty schedules array
        this.allSchedules = [];
        
        // Load all types of schedules from localStorage
        
        // 1. Lab schedules
        const labSchedules = localStorage.getItem('labSchedules');
        if (labSchedules) {
          try {
            const parsedLabData = JSON.parse(labSchedules);
            const labSchedulesArray = Array.isArray(parsedLabData) ? parsedLabData : (parsedLabData.schedules || []);
            this.allSchedules = [...this.allSchedules, ...labSchedulesArray];
          } catch (e) {
            console.error('Error parsing lab schedules from localStorage:', e);
          }
        }
        
        // 2. System Admin schedules
        const sysAdminSchedules = localStorage.getItem('sysadmin_schedules');
        if (sysAdminSchedules) {
          try {
            const parsedSysAdminData = JSON.parse(sysAdminSchedules);
            const sysAdminSchedulesArray = Array.isArray(parsedSysAdminData) ? parsedSysAdminData : (parsedSysAdminData.schedules || []);
            this.allSchedules = [...this.allSchedules, ...sysAdminSchedulesArray];
          } catch (e) {
            console.error('Error parsing system admin schedules from localStorage:', e);
          }
        }
        
        // Remove duplicates based on schedule ID
        const uniqueSchedules = [];
        const seen = new Set();
        this.allSchedules.forEach(schedule => {
          if (!seen.has(schedule.id)) {
            seen.add(schedule.id);
            uniqueSchedules.push(schedule);
          }
        });
        
        this.allSchedules = uniqueSchedules;
        console.log('Total unique schedules loaded:', this.allSchedules.length);
        
        // Apply initial filtering based on selected semester
        this.filterSchedulesBySemester();
      } catch (error) {
        console.error('Error in loadSchedulesFromStorage:', error);
        this.schedules = [];
      }
    },
    filterSchedulesBySemester() {
      console.log('Filtering by semester:', this.selectedSemester);
      
      if (!this.selectedSemester || !this.allSchedules) {
        this.schedules = [];
        return;
      }
      
      // Show both pending and approved schedules in All Schedules view
      this.schedules = this.allSchedules.filter(schedule => 
        schedule.semester === this.selectedSemester &&
        (schedule.status === 'pending' || schedule.status === 'approved')
      );
      
      console.log(`Filtered ${this.schedules.length} schedules for semester ${this.selectedSemester}`);
    },
    showScheduleDetails(dayName, timeSlot) {
      // Find the schedule for this day and timeSlot
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return;
      
      this.selectedSchedule = relevantSchedules[0];
      this.showPopup = true;
    },
    closePopup() {
      this.showPopup = false;
    },
    loadPendingSchedules() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading pending schedules');
          return;
        }
        
        // Load pending schedules logic would go here
        console.log('Loading pending schedules...');
      } catch (error) {
        console.error('Error in loadPendingSchedules:', error);
      }
    },
    loadRegistrationRequests() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading registration requests');
          return;
        }
        
        // Load registration requests logic would go here
        console.log('Loading registration requests...');
      } catch (error) {
        console.error('Error in loadRegistrationRequests:', error);
      }
    },
    approveSelectedSchedule() {
      // Get all pending schedules for current semester across ALL labs
      const pendingSchedules = this.allSchedules.filter(schedule => 
        schedule.status === 'pending' &&
        schedule.semester === this.selectedSemester
        // No lab filter here to include all labs
      );

      if (pendingSchedules.length === 0) {
        alert('No pending schedules to approve for the selected semester');
        return;
      }

      try {
        // Update all pending schedules to approved status
        this.allSchedules = this.allSchedules.map(schedule => {
          if (pendingSchedules.some(pending => pending.id === schedule.id)) {
            return { ...schedule, status: 'approved' };
          }
          return schedule;
        });

        // Try to store in database, but continue with localStorage even if it fails
        pendingSchedules.forEach(schedule => {
          fetch('http://localhost:3000/api/schedules', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ ...schedule, status: 'approved' })
          })
          .then(response => response.json())
          .then(data => {
            console.log('Schedule stored in database successfully:', data);
          })
          .catch(error => {
            console.warn('Could not store schedule in database (continuing with localStorage only):', error);
          });
        });

        // Always update localStorage regardless of database success/failure
        try {
          // Update sysadmin_schedules with approved schedules
          localStorage.setItem('sysadmin_schedules', JSON.stringify(this.allSchedules));

          // Update acad_coor_schedules to reflect the approved status
          let acadCoorSchedules = JSON.parse(localStorage.getItem('acad_coor_schedules') || '[]');
          if (!Array.isArray(acadCoorSchedules)) {
            acadCoorSchedules = [];
          }

          // Update status of approved schedules in acad_coor_schedules
          acadCoorSchedules = acadCoorSchedules.map(schedule => {
            if (pendingSchedules.some(pending => pending.id === schedule.id)) {
              return { ...schedule, status: 'approved' };
            }
            return schedule;
          });

          // Save back to acad_coor_schedules
          localStorage.setItem('acad_coor_schedules', JSON.stringify(acadCoorSchedules));
          
          // Get the currently displayed semester in viewer dashboards
          let currentDisplayedSemester;
          
          // Check viewer_schedules to determine which semester is currently displayed
          const viewerSchedules = JSON.parse(localStorage.getItem('viewer_schedules') || '[]');
          if (Array.isArray(viewerSchedules) && viewerSchedules.length > 0) {
            // Assume all displayed schedules are from the same semester
            currentDisplayedSemester = viewerSchedules[0].semester;
          }

          // If approving a schedule from a different semester than what's currently displayed
          if (currentDisplayedSemester && currentDisplayedSemester !== this.selectedSemester) {
            console.log(`Switching displayed schedules from ${currentDisplayedSemester} to ${this.selectedSemester}`);
            
            // Clear all existing displayed schedules in all dashboards
            localStorage.removeItem('viewer_schedules');
            localStorage.removeItem('lab_schedules');
            localStorage.removeItem('sysadmin_displayed_schedules');
            
            // Get all approved schedules for the new semester
            const approvedSchedulesForNewSemester = this.allSchedules.filter(schedule => 
              schedule.status === 'approved' && 
              schedule.semester === this.selectedSemester
            );
            
            // Update all dashboard views with only the approved schedules from the new semester
            localStorage.setItem('viewer_schedules', JSON.stringify(approvedSchedulesForNewSemester));
            localStorage.setItem('lab_schedules', JSON.stringify(approvedSchedulesForNewSemester));
            localStorage.setItem('sysadmin_displayed_schedules', JSON.stringify(approvedSchedulesForNewSemester));
          } else {
            // If approving schedules from the same semester or there are no currently displayed schedules
            // Just add the newly approved schedules to all dashboard views
            const currentViewerSchedules = JSON.parse(localStorage.getItem('viewer_schedules') || '[]');
            const currentLabSchedules = JSON.parse(localStorage.getItem('lab_schedules') || '[]');
            const currentSysAdminSchedules = JSON.parse(localStorage.getItem('sysadmin_displayed_schedules') || '[]');
            
            // Get only the newly approved schedules
            const newlyApprovedSchedules = pendingSchedules.map(schedule => ({
              ...schedule,
              status: 'approved'
            }));
            
            // Update viewer_schedules
            const updatedViewerSchedules = this.mergeSchedules(currentViewerSchedules, newlyApprovedSchedules);
            localStorage.setItem('viewer_schedules', JSON.stringify(updatedViewerSchedules));
            
            // Update lab_schedules 
            const updatedLabSchedules = this.mergeSchedules(currentLabSchedules, newlyApprovedSchedules);
            localStorage.setItem('lab_schedules', JSON.stringify(updatedLabSchedules));
            
            // Update sysadmin_displayed_schedules
            const updatedSysAdminSchedules = this.mergeSchedules(currentSysAdminSchedules, newlyApprovedSchedules);
            localStorage.setItem('sysadmin_displayed_schedules', JSON.stringify(updatedSysAdminSchedules));
          }
          
          // Refresh the filtered schedules
          this.filterSchedulesBySemester();
          
          // Close the popup if it's open
          this.closePopup();
          
          alert(`${pendingSchedules.length} schedule(s) approved successfully`);
        } catch (storageError) {
          console.error('Error updating localStorage:', storageError);
          alert('Error saving schedules. Please try again.');
        }
      } catch (error) {
        console.error('Error approving schedules:', error);
        alert('Error approving schedules. Please try again.');
      }
    },
    rejectSelectedSchedule() {
      // Get all pending schedules for current semester across ALL labs
      const pendingSchedules = this.allSchedules.filter(schedule => 
        schedule.status === 'pending' &&
        schedule.semester === this.selectedSemester
        // No lab filter here to include all labs
      );

      if (pendingSchedules.length === 0) {
        alert('No pending schedules to reject for the selected semester');
        return;
      }

      // Update the schedule status
      try {
        // Update all pending schedules to draft status (rejected)
        this.allSchedules = this.allSchedules.map(schedule => {
          if (pendingSchedules.some(pending => pending.id === schedule.id)) {
            return { ...schedule, status: 'draft' };
          }
          return schedule;
        });
        
        // Update localStorage
        localStorage.setItem('sysadmin_schedules', JSON.stringify(this.allSchedules));
        
        // Update acad_coor_schedules to reflect the rejected status
        let acadCoorSchedules = JSON.parse(localStorage.getItem('acad_coor_schedules') || '[]');
        if (!Array.isArray(acadCoorSchedules)) {
          acadCoorSchedules = [];
        }

        // Update status of rejected schedules in acad_coor_schedules
        acadCoorSchedules = acadCoorSchedules.map(schedule => {
          if (pendingSchedules.some(pending => pending.id === schedule.id)) {
            return { ...schedule, status: 'draft' };
          }
          return schedule;
        });

        // Save back to acad_coor_schedules
        localStorage.setItem('acad_coor_schedules', JSON.stringify(acadCoorSchedules));
        
        // Refresh the filtered schedules
        this.filterSchedulesBySemester();
        
        // Close the popup if it's open
        this.closePopup();
        
        alert(`${pendingSchedules.length} schedule(s) rejected and sent back to draft`);
      } catch (storageError) {
        console.error('Error updating localStorage:', storageError);
        alert('Error rejecting schedules. Please try again.');
      }
    },
    calculateDurationMinutes(startTime, endTime) {
      try {
        const startMinutes = this.convertTimeToMinutes(startTime);
        const endMinutes = this.convertTimeToMinutes(endTime);
        return endMinutes - startMinutes;
      } catch (error) {
        console.error('Error calculating duration:', error);
        return 60;
      }
    },
    startPolling() {
      // Poll every 5 seconds for updates
      this.pollInterval = setInterval(() => {
        this.checkForUpdates();
      }, 5000);
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    },
    checkForUpdates() {
      try {
        // Get the latest schedules from localStorage
        const latestSchedules = localStorage.getItem('schedules');
        if (!latestSchedules) return;

        const parsedSchedules = JSON.parse(latestSchedules);
        const latestTimestamp = parsedSchedules.timestamp || 0;

        // If this is the first check or if there's a new update
        if (!this.lastUpdateTimestamp || latestTimestamp > this.lastUpdateTimestamp) {
          console.log('New schedule updates detected, refreshing data...');
          this.loadSchedulesFromStorage();
          this.lastUpdateTimestamp = latestTimestamp;
        }
      } catch (error) {
        console.error('Error checking for updates:', error);
      }
    },
    clearAllSchedules() {
      // Clear all schedule-related data from localStorage
      localStorage.removeItem('labSchedules');
      localStorage.removeItem('lab_schedules');
      localStorage.removeItem('sysadmin_schedules');
      localStorage.removeItem('sysadmin_displayed_schedules');
      localStorage.removeItem('acad_coor_schedules');
      localStorage.removeItem('schedules');
      localStorage.removeItem('viewer_schedules');
      localStorage.removeItem('generic_schedules');
      
      // Reset the component's schedule arrays
      this.allSchedules = [];
      this.schedules = [];
      
      console.log('All schedules cleared');
    },
    mergeSchedules(existingSchedules, newSchedules) {
      const seen = new Set();
      const mergedSchedules = [];

      existingSchedules.forEach(schedule => {
        if (!seen.has(schedule.id)) {
          seen.add(schedule.id);
          mergedSchedules.push(schedule);
        }
      });

      newSchedules.forEach(schedule => {
        if (!seen.has(schedule.id)) {
          seen.add(schedule.id);
          mergedSchedules.push(schedule);
        }
      });

      return mergedSchedules;
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  width: 100%;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.dashboard-header {
  margin-bottom: 1.5rem;
}

.welcome-section h2 {
  color: #e91e63;
  font-size: 1.75rem;
  margin: 0;
  font-weight: 500;
}

.dashboard-content {
  display: flex;
  gap: 1.5rem;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.controls-top {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 250px;
}

.search-icon {
  color: #999;
  margin-right: 0.5rem;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 0.9rem;
  width: 100%;
}

.semester-dropdown-wrapper {
  width: 200px;
}

.semester-dropdown {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.6rem 0.5rem;
  font-size: 0.9rem;
  color: #333;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 28px;
  cursor: pointer;
}

.lab-dropdown-wrapper {
  width: 150px;
}

.lab-dropdown {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.6rem 0.5rem;
  font-size: 0.9rem;
  color: #333;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 28px;
  cursor: pointer;
}

.schedule-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  height: 100%;
}

.schedule-table {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-header {
  display: flex;
  border-bottom: 1px solid #eaeaea;
}

.time-header {
  width: 80px;
  padding: 0.75rem 0.5rem;
  text-align: center;
  font-weight: 500;
  color: #e91e63;
  font-size: 0.9rem;
  border-right: 1px solid #eaeaea;
}

.day-headers {
  flex: 1;
  display: flex;
}

.day-header {
  flex: 1;
  padding: 0.75rem 0.5rem;
  text-align: center;
  background-color: #e91e63;
  color: white;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-header:last-child {
  border-right: none;
}

.day-name {
  font-weight: 500;
  font-size: 0.9rem;
}

.table-body {
  display: flex;
  flex: 1;
  overflow-y: auto;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  border-right: 1px solid #eaeaea;
}

.time-slot {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 0.85rem;
}

.days-grid {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  border-right: 1px solid #eaeaea;
}

.day-column:last-child {
  border-right: none;
}

.time-slots {
  display: flex;
  flex-direction: column;
}

.slot {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  position: relative;
}

.schedule-item {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  color: white;
  padding: 0.5rem;
  overflow: hidden;
  z-index: 5;
}

.schedule-item.status-draft {
  background-color: #DD385A;
}

.schedule-item.status-pending {
  background-color: #FFA500;
}

.schedule-item.status-approved {
  background-color: #4CAF50;
}

.schedule-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  cursor: pointer;
  text-align: center;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.schedule-lab {
  font-weight: 600;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
  background-color: rgba(0, 0, 0, 0.15);
  padding: 2px 5px;
  border-radius: 3px;
  display: inline-block;
}

.schedule-time {
  font-size: 0.75rem;
  opacity: 0.9;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.schedule-details {
  font-size: 0.75rem;
  opacity: 0.9;
  white-space: pre-line;
  line-height: 1.4;
}

.table-body::-webkit-scrollbar {
  width: 8px;
}

.table-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-body::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.schedule-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background-color: white;
  border-radius: 8px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.popup-header {
  background-color: #e91e63;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.popup-body {
  padding: 1.5rem;
}

.detail-row {
  margin-bottom: 0.75rem;
  display: flex;
}

.detail-label {
  font-weight: 500;
  width: 100px;
  color: #666;
}

.detail-value {
  flex: 1;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.approve-btn, .reject-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.approve-btn {
  background-color: #4CAF50;
  color: white;
}

.approve-btn:hover {
  background-color: #45a049;
}

.reject-btn {
  background-color: #f44336;
  color: white;
}

.reject-btn:hover {
  background-color: #da190b;
}

.approve-btn svg, .reject-btn svg {
  margin-right: 4px;
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #ff9800;
  color: white;
}

.clear-btn:hover {
  background-color: #f57c00;
}

.clear-btn svg {
  margin-right: 4px;
}
</style>
