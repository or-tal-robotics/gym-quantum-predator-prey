from gym.envs.registration import register

register(
    id='Quantum_Predator_Prey-v0',
    entry_point='gym_quantum_predator_prey.envs:QuantumPredatorPrey',
)