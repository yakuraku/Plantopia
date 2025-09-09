<template>
  <div
    class="home"
    :class="{ 'highlight-left': isLeftActive, 'highlight-right': isRightActive, 'heat-hovered': isHeatHovered }"
    @mousemove="handleMouseMove"
  >
    <!-- Video Background -->
    <video
      ref="videoRef"
      autoplay
      muted
      playsinline
      class="video-background"
      preload="auto"
      @canplay="setVideoSpeed"
    >
      <source src="/plant_watering8.mp4" type="video/mp4">
      Your browser does not support the video tag.
    </video>





    <!-- Hero Section -->
    <Transition name="fade-in" appear>
      <HeroSection
        v-show="showContent"
        @navigate-to-recommendations="goToRecommendations"
        @navigate-to-guides="goToGuides"
        @scroll-to-content="scrollToContent"
        @heat-hover="handleHeatHover"
      />
    </Transition>

    <!-- Content Section -->
    <Transition name="fade-in" appear>
      <div v-show="showContent" class="content-section">
        <div class="home-container">
          <!-- Features Section -->
          <FeaturesSection
            @navigate-to-recommendations="goToRecommendations"
            @navigate-to-dashboard="goToDashboard"
            @navigate-to-journey="goToJourney"
            @navigate-to-plants="goToPlants"
          />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted, ref, computed } from 'vue'

// Import components
import HeroSection from './home/HeroSection.vue'
import FeaturesSection from './home/FeaturesSection.vue'

const router = useRouter()

// Video reference
const videoRef = ref<HTMLVideoElement>()

// Interaction states
const isLeftActive = ref(false)
const isRightActive = ref(false)
const isInteractionEnabled = ref(true) // Control whether interaction is enabled
const isHeatHovered = ref(false) // Control Heat text hover state
const showContent = ref(false) // Control content display animation state

const handleMouseMove = (event: MouseEvent) => {
  // Only handle when interaction is enabled
  if (!isInteractionEnabled.value) return

  const { clientX, clientY, currentTarget } = event
  const { offsetWidth } = currentTarget as HTMLElement
  const halfWidth = offsetWidth / 2

  // Only trigger interaction effects when mouse is in the bottom 70% of the screen
  // This ensures the dividing effect only occurs below the button area
  const windowHeight = window.innerHeight
  if (clientY < windowHeight * 0.3) {
    // Mouse in upper area (title and button area), no interaction triggered
    isLeftActive.value = false
    isRightActive.value = false
    return
  }

  if (clientX < halfWidth) {
    // Mouse on left side - green healthy area
    isLeftActive.value = true
    isRightActive.value = false
  } else {
    // Mouse on right side - yellow drought area
    isLeftActive.value = false
    isRightActive.value = true
  }
}

// Listen to scroll and control interaction effects
const handleScroll = () => {
  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight

  // When scroll distance exceeds 10% of viewport height, start disabling interaction effects
  // This way interaction effects disappear as soon as user starts scrolling
  if (scrollTop > windowHeight * 0.1) {
    isInteractionEnabled.value = false
    isLeftActive.value = false
    isRightActive.value = false
  } else {
    isInteractionEnabled.value = true
  }
}



const goToRecommendations = () => {
  router.push('/recommendations')
}

const goToPlants = (category: 'flowers' | 'vegetables' | 'herbs') => {
  // Pass category as query or path segment depending on your PlantsView routing
  router.push({ path: '/plants', query: { category } })
  // Ensure landing at top of the Plants page
  setTimeout(() => window.scrollTo({ top: 0, behavior: 'auto' }), 0)
}

const goToGuides = () => {
  router.push('/guides')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const goToJourney = () => {
  router.push('/journey')
}

const scrollToContent = () => {
  const contentSection = document.querySelector('.content-section')
  if (contentSection) {
    contentSection.scrollIntoView({ behavior: 'smooth' })
  }
}

const handleHeatHover = (isHovered: boolean) => {
  isHeatHovered.value = isHovered
}

const setVideoSpeed = () => {
  if (videoRef.value) {
    videoRef.value.playbackRate = 1.25
  }
}

// Scroll animations and interaction control
onMounted(() => {
  // Show content after 1 second delay
  setTimeout(() => {
    showContent.value = true
  }, 1000)

  // Add scroll listener
  window.addEventListener('scroll', handleScroll)

  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate')

        // Staggered animation for feature cards and stat cards
        const cards = entry.target.querySelectorAll('.feature-card, .stat-card')
        cards.forEach((card, index) => {
          setTimeout(() => {
            card.classList.add('animate')
          }, index * 150)
        })
      }
    })
  }, observerOptions)

  // Observe all elements that need animation
  const elements = document.querySelectorAll('.features-section')
  elements.forEach((el) => observer.observe(el))
})

// Clean up event listeners
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  scroll-behavior: smooth;
  position: relative;
  transition: all 0.8s ease;
  overflow: hidden; /* Ensure video doesn't overflow */
  background-color: #000; /* Show black background before video loads */
}

/* Video background styles */
.video-background {
  position: fixed;
  top: 0;
  left: -6%; /* Shift left by 6% to align grass with page centerline */
  width: 110vw; /* Increase width to maintain full coverage */
  height: 100vh;
  object-fit: cover; /* Maintain aspect ratio and fill screen */
  object-position: center 25%; /* Adjust to show soil on both large and small screens */
  z-index: 1; /* Needs positive value to display */
}

/* When hovering over Heat text: entire page turns black and white */
.home.heat-hovered .video-background {
  filter: grayscale(100%) contrast(1.2) brightness(0.8);
  transition: filter 0.3s ease;
}

/* Fade in animation */
.fade-in-enter-active {
  transition: all 1.5s ease-out;
}

.fade-in-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.fade-in-enter-to {
  opacity: 1;
  transform: translateY(0);
}



/* Remove color overlay, keep original image colors */
.home::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1); /* Only slight darkening to ensure text readability */
  z-index: 1;
  pointer-events: none;
}



/* Content Section */
.content-section {
  position: relative;
  z-index: 2;
}

.home-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 4rem 2rem 4rem;
  text-align: center;
  position: relative;
  z-index: 2;
}

/* Scroll Animations */
.features-section {
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.features-section.animate {
  opacity: 1;
  transform: translateY(0);
}

.feature-card {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.feature-card.animate {
  opacity: 1;
  transform: translateY(0);
}

.stat-card {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.stat-card.animate {
  opacity: 1;
  transform: translateY(0);
}
</style>
