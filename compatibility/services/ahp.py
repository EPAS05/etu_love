from compatibility.models import Criterion, PairsCriteria, SelectedCriterion, CriterionWeight
import numpy as np

class AHPCalc:
    @staticmethod
    def find_weights(user):
        criteria = list(SelectedCriterion.objects.get(user=user).criteria.all().order_by('id'))
        criteria_ids = {c.id for c in criteria}
        size = len(criteria)

        if size == 0:
            CriterionWeight.objects.filter(user=user).delete()
            return []

        if size == 1:
            crit = criteria[0]
            CriterionWeight.objects.update_or_create(user=user, criterion=crit, defaults={'weight': 1.0, 'consistency_ratio': 0.0})
            return [1.0]

        matrix = np.ones((size, size))

        comparisons = PairsCriteria.objects.filter(
            user=user,
            criterion_a__in=criteria_ids,
            criterion_b__in=criteria_ids
        )

        for comp in comparisons:
            try:
                i = criteria.index(comp.criterion_a)
                j = criteria.index(comp.criterion_b)
                matrix[i][j] = AHPCalc._convert_score(comp.score)
                matrix[j][i] = 1 / matrix[i][j]
            except ValueError:
                continue

        consistency = AHPCalc._check_consistency(matrix)

        if consistency['cr'] > 0.1:
            raise ValueError("Матрица не согласована. CR = {:.2f}".format(consistency['cr']))

        weights = AHPCalc._calculate_eigenvector(matrix)

        for i, criterion in enumerate(criteria):
            CriterionWeight.objects.update_or_create(
                user=user,
                criterion=criterion,
                defaults={
                    'weight': weights[i],
                    'consistency_ratio': consistency['cr']
                }
            )
        return weights

    @staticmethod
    def _convert_score(score):
        conversion = {
            1: 5,
            2: 3,
            3: 1,
            4: 1 / 3,
            5: 1 / 5
        }
        return conversion[score]

    @staticmethod
    def _calculate_eigenvector(matrix):
        geometric_means = []
        for row in matrix:
            product = 1.0
            for value in row:
                product *= value
            geometric_means.append(product ** (1 / len(row)))

        total = sum(geometric_means)
        return [gm / total for gm in geometric_means]

    @staticmethod
    def _check_consistency(matrix):
        n = matrix.shape[0]
        if n == 2:
            return {'ci': 0.0, 'cr': 0.0}
        lambdas = np.linalg.eigvals(matrix)
        lambda_max = max(lambdas).real
        ci = (lambda_max - n) / (n - 1)
        ri = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
        cr = ci / ri.get(n, 1.45)
        return {'ci': ci, 'cr': cr}